import csv
from collections import namedtuple
import json

from django.db import models

from inventory import models as inv_models
from inventory.incoming_actions import create
from scrap import commands


class Command(commands.Command):
    script_name = "ingest_common_item_names"
    help_text = """
    Add common item names from a tsv exported from the inventory Google Sheet.
    """
    data_row_fields = [
        "question", "count", "category", "sizes", "item_name", "better_item_name", "single_serving", "common_name",
        "first_other_name", "second_other_name", "third_other_name", "location"]

    def initialize_data(self):
        data = {
            "records": 0,
            "common_name_dict": {},
            "categories": set(),
        }
        return data

    def print_examples(self, data):
        example_a = 0
        example_b = 0
        example_c = 0
        example_d = 0
        for cn_key in data["common_name_dict"]:
            cn_dict = data["common_name_dict"][cn_key]
            printed = False
            if not printed and example_a < 3 and len(cn_dict["common_names"]) > 1:
                print("multiple common names")
                print(json.dumps(cn_dict, indent=2, sort_keys=True, default=str))
                example_a += 1
                printed = True
            if not printed and example_b < 3 and len(cn_dict["raw_item_names"]) > 1:
                print("multiple raw item names")
                print(json.dumps(cn_dict, indent=2, sort_keys=True, default=str))
                example_b += 1
                printed = True
            if not printed and example_c < 3 and max([len(v) for v in cn_dict["raw_item_names"].values()]) >= 1:
                print("has better raw item names")
                print(json.dumps(cn_dict, indent=2, sort_keys=True, default=str))
                example_c += 1
                printed = True
            if not printed and example_d < 3 and len(cn_dict["categories"]) > 1:
                print("categories")
                print(json.dumps(cn_dict, indent=2, sort_keys=True, default=str))
                example_d += 1
                printed = True
            if example_a > 3 and example_b > 3 and example_c > 3 and example_d > 3:
                break
        print(f"multi cn = {example_a}, multi raw = {example_b}, better = {example_c}, category = {example_d}")

    def process_categories(self, data):
        print(f"all categories: {data['categories']}")
        created_count = 0
        created_list = []
        categories = {}
        for category in data['categories']:
            category_obj, created = inv_models.Category.objects.get_or_create(name=category)
            if created:
                created_count += 1
                created_list.append(category)
            categories[category] = category_obj
        if created_list:
            print(f"Created {created_count} new categories: {created_list}")
        else:
            print("no new categories in the file.")
        return categories

    def process_common_item_names(self, data, category_dict):
        for cn_key, cn_dict in data["common_name_dict"].items():
            print(f"CommonItemNameGroup {cn_dict['primary_common_name']!r}")
            category_str = list(cn_dict["categories"])[0]
            new_cn = []
            new_cn_str = []
            group_set = set()
            primary_set = set()
            primary_cn = None
            for cn_str in cn_dict["common_names"]:
                is_primary_name_str = cn_str == cn_dict["primary_common_name"]
                cn, created = inv_models.CommonItemName.objects.get_or_create(name=cn_str)
                if created:
                    new_cn.append(cn)
                    new_cn_str.append(cn_str)
                else:
                    if cn.common_item_name_group:
                        group_set.add(cn.common_item_name_group)
                    if cn.primary_groups.count() > 0:
                        primary_set.update(set(cn.primary_groups.all()))
                        if not is_primary_name_str:
                            pass
                if is_primary_name_str:
                    primary_cn = cn
            if new_cn:
                print(f"\tCreated {len(new_cn)} CommonItemNames.  {new_cn_str}")
            if len(group_set) == len(primary_set) == 1 and group_set == primary_set:
                # all good.  group and primary sets are 1 and the same group object.
                cn_group = group_set.pop()
                for cn in new_cn:
                    cn.common_item_name_group = cn_group
                uncommon_item_names_from_file = set(cn_dict["raw_item_names"].keys())
                uncommon_item_names_from_file.update(cn_group.uncommon_item_names)
                if uncommon_item_names_from_file != set(cn_group.uncommon_item_names):
                    cn_group.uncommon_item_names = list(uncommon_item_names_from_file)
                    cn_group.save()
                inv_models.CommonItemName.objects.bulk_update(new_cn, fields=('common_item_name_group', ))
            elif len(group_set) == len(primary_set) == 0:
                # No group.  All are new?
                cn_group = inv_models.CommonItemNameGroup.objects.create(
                    category=category_dict[category_str], name=primary_cn,
                    uncommon_item_names=list(cn_dict["raw_item_names"].keys()))
                print(f"\tCreated CommonItemNameGroup(name={primary_cn.name!r}, category={category_str!r})")
                for cn in new_cn:
                    cn.common_item_name_group = cn_group
                cn_update = inv_models.CommonItemName.objects.bulk_update(new_cn, fields=('common_item_name_group', ))
                print(f"\tUpdated {cn_update} CommonItemNames to use the new group.")
            else:
                # broken group relations.  Needs manual intervention.
                print(f"!!! group_set and primary_set are not valid. {group_set}, {primary_set}")

    def process_output(self, data):
        print(f"records = {data['records']}")
        """
        {
          "categories": "{'canned & dry'}",
          "common_names": "{'pam', 'pan spray', 'cooking spray', 'nonstick spray'}",
          "primary_common_name": "nonstick spray",
          "raw_item_names": {
            "crisco pan coating release arsl": "set()",
            "sys cls pan coating arsl": "set()",
            "sys imp pan coating arsl butter i": "set()",
            "sys imp pan coating arsl conc": "set()"
          }
        }
        {
          "categories": "{'canned & dry'}",
          "common_names": "{'flour', 'all purpose flour'}",
          "primary_common_name": "flour",
          "raw_item_names": {
            "sys cls flour all purp h&r bl e": "{'sysco classic flour all purpose hotel and restaurant bleached enriched malted'}"
          }
        }
        """
        self.print_examples(data)
        category_dict = self.process_categories(data)
        self.process_common_item_names(data, category_dict)
        create.assign_common_item_names()
        print("done.")

    def process_row(self, row_number, named_row, data):
        data["records"] += 1
        common_name_fields = ["common_name", "first_other_name", "second_other_name", "third_other_name"]
        common_names = set(getattr(named_row, cnf) for cnf in common_name_fields if getattr(named_row, cnf))
        if not named_row.common_name:
            return
        if named_row.common_name not in data["common_name_dict"]:
            data["common_name_dict"][named_row.common_name] = {
                "primary_common_name": named_row.common_name,
                "common_names": set(),
                "raw_item_names": {},
                "categories": set(),
            }
        cn_dict = data["common_name_dict"][named_row.common_name]

        cn_dict["common_names"].update(common_names)
        cn_dict["categories"].add(named_row.category)
        data["categories"].add(named_row.category)

        if named_row.item_name not in cn_dict["raw_item_names"]:
            cn_dict["raw_item_names"][named_row.item_name] = set()
        if named_row.better_item_name:
            cn_dict["raw_item_names"][named_row.item_name].add(named_row.better_item_name)
