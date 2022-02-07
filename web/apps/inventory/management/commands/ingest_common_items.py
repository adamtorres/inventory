import csv
from collections import namedtuple

from django.core.management.base import BaseCommand

from inventory import models as inv_models

DataRow = namedtuple("DataRow", [
    "question", "count", "category", "sizes", "item_name", "better_item_name", "single_serving", "common_name",
    "first_other_name", "second_other_name", "third_other_name", "location"])


class Command(BaseCommand):
    help = """
    Load CommonItems and CommonItemOtherName from a file.  Will not add duplicates and will not remove existing.
    Example Usage:
        python manage.py ingest_common_items --datafile=<filename>
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-f',
            '--datafile',
            action='store',
            dest='datafile',
            help="TSV data file"
        )

    def dump_stats(self, data):
        print(f"Total records: {data['records']}")
        for category, category_data in data["categories"].items():
            print(f"\tCategory: {category}")
            print(f"\tRecords: {len(category_data)}")
        print(f"Common names: {len(data['common_names'])}")

    def handle(self, *args, **options):
        datafile = options.get('datafile')
        data = {
            "categories": {},
            "records": 0,
            "common_names": {},
            "locations": {},
        }
        args = {
            "data": data,
        }
        self.process_datafile(datafile, self.process_row, args=args)
        self.dump_stats(data)
        self.upsert_categories(data["categories"])
        self.upsert_locations(data["locations"])
        self.upsert_common_items(data["common_names"])
        self.update_categories(data["categories"])
        self.update_common_item_locations(data["locations"])

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
        _data = {
            "common_names": {
                "primary common name": {"set", "of", "other", "names", },
                "ground beef": {"hamburger meat", "burger meat", },
                "orange juice carton": {"oj carton", },
            }
        }
        self.process_categories(row, data["categories"])
        self.process_common_names(row, data["common_names"])
        self.process_locations(row, data["locations"])

    def process_categories(self, row, categories):
        # Goal: keys = category names.  values = set of common names.
        cat_lower = row.category.lower()
        if cat_lower not in categories:
            categories[cat_lower] = set()
        categories[cat_lower].add(row.common_name.lower())

    def process_common_names(self, row, common_names):
        cn_lower = row.common_name.lower()
        if cn_lower not in common_names:
            common_names[cn_lower] = set()
        # Update the set for the common name with a lower/strip set of other names.  Excludes blanks.
        common_names[cn_lower].update([
            n.lower().strip() for n in [row.first_other_name, row.second_other_name, row.third_other_name]
            if n.strip()])

    def process_locations(self, row, locations):
        l_lower = row.location.lower()
        if l_lower not in locations:
            locations[l_lower] = set()
        locations[l_lower].add(row.common_name.lower())

    def generic_upsert(self, model, new_data, data_name):
        existing_values = set(model.objects.filter(name__in=new_data).values_list('name', flat=True))
        print(f"existing {data_name} values from file: {len(existing_values)}")
        new_values = set(new_data).difference(existing_values)
        print(f"new {data_name} values from file: {len(new_values)}")
        if new_values:
            new_items = [inv_models.CommonItem(name=n) for n in new_values]
            model.objects.bulk_create(new_items)

    def update_categories(self, categories):
        for category, category_data in categories.items():
            print(f"Category: {category}")
            print(f"\tFile contains {len(category_data)} common names")
            category_obj = inv_models.Category.objects.filter(name=category).first()
            existing_names = category_obj.common_items.filter(name__in=category_data).values_list('name', flat=True)
            print(f"\tExisting {len(existing_names)} common items on category")
            new_names = set(category_data).difference(existing_names)
            print(f"\tAdding {len(new_names)} common items to category")
            new_common_items = inv_models.CommonItem.objects.filter(name__in=new_names)
            category_obj.common_items.add(*list(new_common_items))

    def update_common_item_locations(self, locations):
        for location_name, location_set in locations.items():
            print(f"Location: {location_name}")
            location_obj = inv_models.Location.objects.filter(name=location_name).first()
            existing_names = location_obj.common_items.filter(name__in=location_set).values_list('name', flat=True)
            print(f"\tExisting {len(existing_names)} common items on location")
            new_names = set(location_set).difference(existing_names)
            print(f"\tAdding {len(new_names)} common items to location")
            new_common_items = inv_models.CommonItem.objects.filter(name__in=new_names)
            location_obj.common_items.add(*list(new_common_items))

    def upsert_categories(self, categories):
        self.generic_upsert(inv_models.Category, categories, "category")

    def upsert_common_items(self, common_names):
        self.generic_upsert(inv_models.CommonItem, common_names, "common name")

        new_other_item_names = []
        for common_name, other_names in common_names.items():
            if not other_names:
                continue
            ci = inv_models.CommonItem.objects.get(name=common_name)
            existing_other_names = set(ci.other_names.filter(name__in=other_names).values_list('name', flat=True))
            new_other_names = other_names.difference(existing_other_names)
            new_other_item_names.extend([
                inv_models.CommonItemOtherName(common_item=ci, name=non)
                for non in new_other_names
            ])
        print(f"Total new other names: {len(new_other_item_names)}")
        if new_other_item_names:
            inv_models.CommonItemOtherName.objects.bulk_create(new_other_item_names)

    def upsert_locations(self, locations):
        self.generic_upsert(inv_models.Location, locations, "location")
