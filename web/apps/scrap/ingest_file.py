from collections import namedtuple
import csv

from django.core.management.base import BaseCommand
from django.utils import timezone

from incoming import models as inc_models
# from inventory import models as inv_models


class Command(BaseCommand):
    script_name = "ingest_file"
    help_text = "Generic help text"
    replace_empty_str_fields = []
    replace_empty_str_value = 0

    def __init__(self, stdout=None, stderr=None, no_color=False, force_color=False):
        super().__init__(stdout=stdout, stderr=stderr, no_color=no_color, force_color=force_color)
        self.help = f"""{self.help_text}
        Example usage:
            python manage.py {self.script_name} --datafile <filename>
        """
        self.DataRow = namedtuple("DataRow", [
            "source", "order_date", "delivery_date", "customer_number", "department", "PO_text", "order_number",
            "line_item_number", "category", "quantity", "pack_quantity", "unit_size", "item_name", "extra_crap",
            "item_code", "pack_cost", "pack_tax", "extended_cost", "total_weight", "handwritten_notes", "scan_file"])
        self.field_index = {field: f for f, field in enumerate(self.DataRow._fields)}

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
            '--case',
            action='store',
            dest='case',
            help="Should the case of the entire row be UPPER, LOWER, or ASIS(default)?",
            choices=['UPPER', 'LOWER', 'ASIS'],
            default='ASIS'
        )
        parser.add_argument(
            '--skip-lines',
            action='store',
            dest='skip_lines',
            help="Number of lines to skip at the top of the file?",
            type=int,
            default=0,
        )

    def handle(self, *args, **options):
        datafile = options.get('datafile')
        case = options.get('case')
        skip_lines = options.get('skip_lines')

        data = {}
        args = {
            "data": data,
        }
        self.process_datafile(datafile, case=case, skip_lines=skip_lines)
        self.process_output(data)

    def process_datafile(self, datafile, case="ASIS", skip_lines=0):
        case_func = {
            "UPPER": lambda x: x.upper(),
            "LOWER": lambda x: x.lower(),
        }.get(case, lambda x: x)
        with open(datafile, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quotechar='|')
            for r, row in enumerate(reader):
                while r < skip_lines:
                    continue
                if case in ["UPPER", "LOWER"]:
                    row = [case_func(field) for field in row]
                row = self.preclean_row(row)
                named_row = self.DataRow(*row)
                named_row = self.postclean_row(named_row)
                self.process_row(r, named_row)

    def process_output(self, data):
        """
        Override this to deal with the collected data after all rows are processed.
        """
        pass

    def process_row(self, row_number, named_row):
        """
        Called per row read in.
        """
        pass

    def preclean_row(self, raw_row_data):
        """
        Use this to apply any special column validations/conversions/suppressions/etc.
        Returns a list with values per field.  Must have the same number of values each time.
        This happens before cramming the data into the namedtuple.
        """

        return self.replace_empty_str(raw_row_data)

    def postclean_row(self, named_row):
        """
        This is to apply any special column validations/conversions/suppressions/etc after being converted to a
        namedtuple.  Remaking the named tuple here takes a few steps.  For example, finding a field containing an empty
        string and changing it to a 0.
        Best to do this in preclean_row.  Might remove this step later.
            tmp = named_row._asdict()
            tmp['field_that_does_not_like_empty_string'] = 0
            named_row = DataRow(**tmp)
        """
        return named_row

    def replace_empty_str(self, raw_row_data):
        for field_name in self.replace_empty_str_fields:
            if raw_row_data[self.field_index[field_name]] == '':
                raw_row_data[self.field_index[field_name]] = self.replace_empty_str_value
        return raw_row_data
