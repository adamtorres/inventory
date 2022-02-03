import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from incoming import models as inc_models
# from inventory import models as inv_models


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

    def handle(self, *args, **options):
        datafile = options.get('datafile')
        add_new_sources = options.get('add_new_sources')

        headers = {}
        data = {}
        with open(datafile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for r, row in enumerate(reader):
                if r == 0:
                    for idx, field_name in enumerate(row):
                        headers[field_name] = idx
                    continue
                source = row[headers["vendor"]]
                item = row[headers["item"]]
                item_code = row[headers["item code"]]
                if source not in data:
                    data[source] = {"records": 0, "items_by_name": {}, "items_by_code": {}}
                data[source]["records"] += 1
                if item not in data[source]["items_by_name"]:
                    data[source]["items_by_name"][item] = 0
                data[source]["items_by_name"][item] += 1
                if item_code not in data[source]["items_by_code"]:
                    data[source]["items_by_code"][item_code] = 0
                data[source]["items_by_code"][item_code] += 1
                print(f"{r}, {row}")
        for source, source_data in data.items():
            print("=========")
            print(f"Source: {source}")
            print(f"Total records: {source_data['records']}")
            for item in source_data["items_by_name"]:
                print(f"  {item!r} == {source_data['items_by_name'][item]}")