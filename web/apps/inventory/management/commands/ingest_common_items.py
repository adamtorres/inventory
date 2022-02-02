import csv

from django.core.management.base import BaseCommand

from incoming import models as inc_models
from inventory import models as inv_models


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

    def handle(self, *args, **options):
        datafile = options.get('datafile')
        fields = {
            'question': 0,
            'count': 1,
            'category': 2,
            'sizes': 3,
            'item': 4,
            'single serving': 5,
            'common_name': 6,
            'other_name_0': 7,
            'other_name_1': 8,
            'other_name_2': 9,
        }
        common_names = dict()
        with open(datafile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for row in reader:
                common_name = row[fields['common_name']].lower()
                other_names = [
                    row[fields[f'other_name_{c}']].lower()
                    for c in range(3)
                    if row[fields[f'other_name_{c}']]]
                if common_name not in common_names:
                    common_names[common_name] = set()
                common_names[common_name].update(other_names)
        # should now have a dict with common_name keys and distinct other_names.
        existing_common_names = set(
            inv_models.CommonItem.objects.filter(name__in=common_names).values_list('name', flat=True))
        new_common_names = set(common_names).difference(existing_common_names)

        new_common_items = [inv_models.CommonItem(name=n) for n in new_common_names]
        inv_models.CommonItem.objects.bulk_create(new_common_items)

        for common_name, other_names in common_names.items():
            if not other_names:
                continue
            ci = inv_models.CommonItem.objects.get(name=common_name)
            existing_other_names = set(ci.other_names.filter(name__in=other_names).values_list('name', flat=True))
            new_other_names = other_names.difference(existing_other_names)
            new_other_item_names = [
                inv_models.CommonItemOtherName(common_item=ci, name=non)
                for non in new_other_names
            ]
            ci.other_names.bulk_create(new_other_item_names)
