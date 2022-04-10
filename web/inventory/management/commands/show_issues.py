from django.core.management.base import BaseCommand

from inventory import models as inv_models
from inventory.incoming_actions import clean


def failed_validate_unit_size():
    failed_unit_sizes = set([i.unit_size for i in inv_models.RawIncomingItem.objects.failed('validate_unit_size')])
    print("These are the unit_sizes of the failed records:")
    print(failed_unit_sizes)
    print()


def failed_validate_item_combos():
    print("These items failed validate_item_combos:")
    clean.console_report_on_failed_validate_item_combos()
    print()


def missing_common_item_name():
    print("These items need common names:")
    inv_models.RawItem.reports.console_missing_common_item_name()
    print()


class Command(BaseCommand):
    help = """
    Simply shows a variety of failed information.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            dest='show_all',
            help="Show all of the failed reports",
            default=False
        )
        parser.add_argument(
            '--unit-size',
            action='store_true',
            dest='show_unit_size',
            help="Unit sizes which failed validation - likely unrecognized values.",
            default=False
        )
        parser.add_argument(
            '--item-combo',
            action='store_true',
            dest='show_item_combo',
            help="Item combos which failed validation - 4 fields make up a unique constraint but a distinct is done on "
                 "more than those 4 fields.",
            default=False
        )
        parser.add_argument(
            '--common-name',
            action='store_true',
            dest='show_common_name',
            help="Items which are missing a common name.",
            default=False
        )

    def handle(self, *args, **options):
        if options['show_all']:
            options.update({
                'show_unit_size': True,
                'show_item_combo': True,
                'show_common_name': True,
            })

        if options['show_unit_size']:
            failed_validate_unit_size()

        if options['show_item_combo']:
            failed_validate_item_combos()

        if options['show_common_name']:
            missing_common_item_name()
