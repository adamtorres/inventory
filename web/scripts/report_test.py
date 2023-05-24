from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from inventory import reports


def run():
    with monkey_patch_cursordebugwrapper(print_sql=True, confprefix="SHELL_PLUS", print_sql_location=False):
        reports.SourceItemNamesAndQuantities.get_groupings()
