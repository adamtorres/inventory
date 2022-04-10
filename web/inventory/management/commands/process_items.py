from django.core.management import call_command
from django.core.management.base import BaseCommand

from inventory import incoming_actions, models as inv_models


class Command(BaseCommand):
    help = """
    To process all ready items completely:
    python manage.py process_items --all
    
    To process ready items from a certain step and only for one further step:
    python manage.py process_items --[clean|calculate|create|import]
    """

    def add_arguments(self, parser):
        parser.add_argument(
            '-i',
            '--incoming-items-data-file',
            action='store',
            dest='incoming_items_data_file',
            help="Incoming items data file",
            default=None
        )
        parser.add_argument(
            '-c',
            '--common-item-names-data-file',
            action='store',
            dest='common_item_names_data_file',
            help="Common item name data file",
            default=None
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='run_all',
            help="Run all of the steps",
            default=False
        )
        parser.add_argument(
            '--clean',
            action='store_true',
            dest='run_clean',
            help="Run the clean step",
            default=False
        )
        parser.add_argument(
            '--calculate',
            action='store_true',
            dest='run_calculate',
            help="Run the calculate step",
            default=False
        )
        parser.add_argument(
            '--create',
            action='store_true',
            dest='run_create',
            help="Run the create step",
            default=False
        )
        parser.add_argument(
            '--import',
            action='store_true',
            dest='run_import',
            help="Run the import step",
            default=False
        )

    def handle(self, *args, **options):
        if options['run_all']:
            options.update({
                'run_clean': True,
                'run_calculate': True,
                'run_create': True,
                'run_import': True,
            })

        if options['incoming_items_data_file']:
            call_command('ingest_items', datafile=options['incoming_items_data_file'])
            inv_models.console_show_counts()

        if options['run_clean']:
            print("Running clean step")
            incoming_actions.do_clean(2000)
            inv_models.console_show_counts()

        if options['run_calculate']:
            print("Running calculate step")
            incoming_actions.do_calculate(2000)
            inv_models.console_show_counts()

        if options['run_create']:
            print("Running create step")
            incoming_actions.do_create(0)
            inv_models.console_show_counts()

        if options['incoming_items_data_file']:
            call_command('ingest_common_item_names', datafile=options['common_item_names_data_file'])
            inv_models.console_show_counts()

        if options['run_import']:
            print("Running import step")
            incoming_actions.do_import(0)
            inv_models.console_show_counts()

        print("done.")
