from collections import namedtuple
import csv

from django.core.management.base import BaseCommand
from django.db.models import functions

from incoming import models as inc_models
from inventory import models as inv_models


DataRow = namedtuple("DataRow", [
    "question", "count", "category", "sizes", "item_name", "better_item_name", "single_serving", "common_name",
    "first_other_name", "second_other_name", "third_other_name", "location"])


class Command(BaseCommand):
    help = """
    Load incoming.Items from a file.  The input can have duplicates.  This will work out a unique list.
    Example Usage:
        python manage.py apply_common_items --datafile=<filename>
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--datafile',
            action='store',
            dest='datafile',
            help="TSV data file",
            required=True
        )

    def dump_stats(self, data):
        print(f"Total records: {data['records']}")
        for category, category_data in data["categories"].items():
            print(f"\tCategory: {category}")
            print(f"\tRecords: {category_data['records']}")

    def handle(self, *args, **options):
        datafile = options.get('datafile')
        data = {
            "categories": {},
            "records": 0,
            "common_names": {},
        }
        args = {
            "data": data,
        }
        self.process_datafile(datafile, self.process_row, args=args)
        self.dump_stats(data)
        self.update_better_names(data)
        self.update_categories(data)
        self.update_common_items(data)

    def process_datafile(self, datafile, row_func, args=None, skip_first_row=True):
        with open(datafile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for r, row in enumerate(reader):
                if skip_first_row and r == 0:
                    continue
                named_row = DataRow(*row)
                row_func(r, named_row, **args)

    def process_row(self, row_number, row, data=None):
        data["records"] += 1
        if row.category not in data["categories"]:
            data["categories"][row.category] = {
                "records": 0,
                "items": {},
            }
        data["categories"][row.category]["records"] += 1
        data["categories"][row.category]["items"][row.item_name] = {
            "better_item_name": row.better_item_name,
            "common_name": row.common_name,
            "first_other_name": row.first_other_name,
            "second_other_name": row.second_other_name,
            "third_other_name": row.third_other_name,
        }

        if row.common_name not in data["common_names"]:
            data["common_names"][row.common_name] = {
                "categories": {},
                "records": 0,
            }
        data["common_names"][row.common_name]["records"] += 1
        if row.category not in data["common_names"][row.common_name]["categories"]:
            data["common_names"][row.common_name]["categories"][row.category] = {
                "items": []
            }
        data["common_names"][row.common_name]["categories"][row.category]["items"].append(row.item_name)

    def update_better_names(self, data):
        for category, category_data in data["categories"].items():
            print(f"Category: {category}")
            items_to_update = []
            for item_name, item_dict in category_data["items"].items():
                for item in inc_models.Item.objects.filter(name__iexact=item_name).all():
                    if item.better_name != item_dict["better_item_name"]:
                        item.better_name = item_dict["better_item_name"]
                        items_to_update.append(item)
            if items_to_update:
                print(f"\tUpdating {len(items_to_update)} items.")
                inc_models.Item.objects.bulk_update(items_to_update, ['better_name'])

    def update_categories(self, data):
        categories = {c.name.lower(): c for c in inv_models.Category.objects.all()}
        common_items_to_update = []
        for common_name, common_name_data in data["common_names"].items():
            if len(common_name_data["categories"]) != 1:
                print(f"Common Name {common_name} has multiple categories: {common_name_data['categories'].keys()}")
                # TODO: Flesh this out.  Currently not an issue so not spending time on it yet.
                continue
            category = list(common_name_data["categories"])[0]
            category_obj = categories[category.lower()]
            for common_item in inv_models.CommonItem.objects.filter(name__iexact=common_name):
                if not common_item.category:
                    common_item.category = category_obj
                    common_items_to_update.append(common_item)
                elif common_item.category != category_obj:
                    print(f"CommonItem {common_item} has category {common_item.category} but should be {category}.")
        if common_items_to_update:
            print(f"\tUpdating {len(common_items_to_update)} common items.")
            inv_models.CommonItem.objects.bulk_update(common_items_to_update, ['category'])

    def update_common_items(self, data):
        for category, category_data in data["categories"].items():
            print(f"Category: {category}")
            items_to_update = []
            for item_name, item_dict in category_data["items"].items():
                for item in inc_models.Item.objects.filter(name__iexact=item_name).all():
                    if not item.common_item:
                        specified_common_names = [
                            item_dict["common_name"], item_dict["first_other_name"], item_dict["second_other_name"],
                            item_dict["third_other_name"]]
                        specified_common_names_lower = map(lambda x: x.lower(), specified_common_names)
                        common_items = inv_models.CommonItem.objects.annotate(
                            name_lower=functions.Lower('name')).filter(name_lower__in=specified_common_names_lower)
                        if not common_items:
                            print(f"Did not find common items matching any of: {specified_common_names}")
                            continue
                        common_item = common_items.first()
                        item.common_item = common_item
                        items_to_update.append(item)
            if items_to_update:
                print(f"\tUpdating {len(items_to_update)} items.")
                inc_models.Item.objects.bulk_update(items_to_update, ['common_item'])
