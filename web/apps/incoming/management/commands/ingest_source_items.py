from collections import namedtuple
import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from incoming import models as inc_models
# from inventory import models as inv_models


DataRow = namedtuple("DataRow", [
    "source", "order_date", "delivery_date", "customer_number", "department", "PO_text", "order_number",
    "line_item_number", "category", "quantity", "pack_quantity", "unit_size", "item_name", "extra_crap",
    "item_code", "pack_cost", "pack_tax", "extended_cost", "total_weight", "handwritten_notes", "scan_file"])


class Command(BaseCommand):
    help = """
    Load incoming.Items from a file.  The input can have duplicates.  This will work out a unique list.
    Example Usage:
        python manage.py ingest_source_items --datafile=<filename>
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
        parser.add_argument(
            '-a',
            '--add-new-sources',
            action='store_true',
            dest='add_new_sources',
            help=(
                "Adds the specified sources if not found.  Would normally fail when a source does not exist in case "
                "there are typos.")
        )

    def dump_stats(self, data, outer_field, inner_field, add_new_sources=False):
        group_value = f"grouped by {outer_field}"
        inner_group_value = f"{inner_field}s"
        for source_name, source_data in data.items():
            print("=========")
            print(f"Source: {source_name}")
            print(f"Total records: {source_data['records']}")
            print(f"Distinct items by {outer_field}: {len(source_data[group_value])}")
            if add_new_sources:
                source_obj, created = inc_models.Source.objects.get_or_create(
                    name__iexact=source_name, defaults={"name": source_name})
                if created:
                    print("! Created new source object.")
            else:
                source_obj = inc_models.Source.objects.filter(name__iexact=source_name).first()
            if not source_obj:
                # If there isn't a source object, there's no point going through the rest of the
                continue
            for outer_value in source_data[group_value]:
                for inner_value in source_data[group_value][outer_value][inner_group_value]:
                    pack_size_unit_size_combos = set()
                    for order in source_data[group_value][outer_value][inner_group_value][inner_value]:
                        pack_size_unit_size_combos.add(f"{order['pack_quantity']}, {order['unit_size']}")
                    if len(pack_size_unit_size_combos) > 1:
                        print(f"{outer_field}: {outer_value}")
                        print(f"\t{inner_field}: {inner_value}")
                        for psusc in pack_size_unit_size_combos:
                            print(f"\t\t{psusc}")
                # inc_models.Item(source=source_obj, name=item_name, pack_quantity='', unit_size='')

    def handle(self, *args, **options):
        datafile = options.get('datafile')
        add_new_sources = options.get('add_new_sources')

        outer_field = 'item_code'
        inner_field = 'item_name'
        data = {}
        args = {
            "data": data,
            "outer_field": outer_field,
            "inner_field": inner_field,
        }
        self.process_datafile(datafile, self.process_row, args=args)
        self.dump_stats(data, outer_field, inner_field, add_new_sources=add_new_sources)

    def probably_will_not_use(self, source_name, add_new_source=False):
        """
        Initially used this when expecting the command to ingest only one source's items at a time.  Might use something
        from this for when adding sources from the combined file.
        """
        created = False
        if not source_name:
            # No source specified.  Use the only one available.  If zero or more than one, fail.
            source_count = inc_models.Source.objects.count()
            if source_count < 1:
                raise inc_models.Source.DoesNotExist()
            if source_count > 1:
                raise inc_models.Source.MultipleObjectsReturned()
            source = inc_models.Source.objects.first()
            source_name = source.name
        else:
            if add_new_source:
                source, created = inc_models.Source.objects.get_or_create(
                    name__iexact=source_name,
                    defaults={"name": source_name})
            else:
                source = inc_models.Source.objects.get(name__iexact=source_name)
        return source_name, source, created

    def process_datafile(self, datafile, row_func, args=None, skip_first_row=True):
        with open(datafile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for r, row in enumerate(reader):
                if skip_first_row and r == 0:
                    continue
                named_row = DataRow(*row)
                row_func(r, named_row, **args)

    def process_row(self, row_number, row, data=None, outer_field=None, inner_field=None):
        inner_value = getattr(row, inner_field)
        outer_value = getattr(row, outer_field)
        group_value = f"grouped by {outer_field}"
        inner_group_value = f"{inner_field}s"

        if row.source not in data:
            data[row.source] = {"records": 0, group_value: {}}
        data[row.source]["records"] += 1

        if outer_value not in data[row.source][group_value]:
            data[row.source][group_value][outer_value] = {"records": 0, inner_group_value: {}}
        data[row.source][group_value][outer_value]["records"] += 1

        if inner_value not in data[row.source][group_value][outer_value][inner_group_value]:
            data[row.source][group_value][outer_value][inner_group_value][inner_value] = []
        data[row.source][group_value][outer_value][inner_group_value][inner_value].append(row._asdict())
