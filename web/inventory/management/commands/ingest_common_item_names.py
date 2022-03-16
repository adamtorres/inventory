import csv
from collections import namedtuple
import json

from inventory import models as inv_models
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
            category = list(cn_dict["categories"])[0]
            cn_group = inv_models.CommonItemNameGroup.objects.create(category=category_dict[category])
            cin_to_create = []
            for cn_str in cn_dict["common_names"]:
                cin_to_create.append(inv_models.CommonItemName(name=cn_str, common_item_name_group=cn_group))
            created_cin = inv_models.CommonItemName.objects.bulk_create(cin_to_create)
            for cn in created_cin:
                if cn.name == cn_dict["primary_common_name"]:
                    cn_group.name = cn
                    cn_group.save()

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

        print("done.")

    def process_row(self, row_number, named_row, data):
        data["records"] += 1
        common_name_fields = ["common_name", "first_other_name", "second_other_name", "third_other_name"]
        common_names = set(getattr(named_row, cnf) for cnf in common_name_fields if getattr(named_row, cnf))
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
