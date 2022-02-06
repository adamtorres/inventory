from collections import namedtuple
import csv

from django.core.management.base import BaseCommand

from incoming import models as inc_models
from inventory import models as inv_models


DataRow = namedtuple("DataRow", [
    "question", "count", "category", "sizes", "item_name", "better_item_name", "single_serving", "common_name",
    "first_other_name", "second_other_name", "third_other_name"])


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
            print(f"\tRecords: {category_data['records']}")
        print(f"Common names: {len(data['common_names'])}")

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
        self.upsert_common_items(data)

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
        cn_lower = row.common_name.lower()
        if cn_lower not in data["common_names"]:
            data["common_names"][cn_lower] = set()
        # Update the set for the common name with a lower/strip set of other names.  Excludes blanks.
        data["common_names"][cn_lower].update([
            n.lower().strip() for n in [row.first_other_name, row.second_other_name, row.third_other_name]
            if n.strip()])

    def upsert_common_items(self, data):
        existing_common_names = set(
            inv_models.CommonItem.objects.filter(name__in=data["common_names"]).values_list('name', flat=True))
        print(f"existing common names from file: {len(existing_common_names)}")
        new_common_names = set(data["common_names"]).difference(existing_common_names)
        print(f"new common names from file: {len(new_common_names)}")
        if new_common_names:
            new_common_items = [inv_models.CommonItem(name=n) for n in new_common_names]
            inv_models.CommonItem.objects.bulk_create(new_common_items)

        new_other_item_names = []
        for common_name, other_names in data["common_names"].items():
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
