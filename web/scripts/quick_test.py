# From django_extensions/management/commands/shell_plus.py line 517
# with monkey_patch_cursordebugwrapper(
#         print_sql=options["print_sql"] or print_sql,
#         truncate=truncate,
#         print_sql_location=options["print_sql_location"],
#         confprefix="SHELL_PLUS"):

from django.db import models
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from incoming import models as inc_models


def run():
    print((("=" * 150) + "\n") * 3)
    # The configprefix is used to get some settings.  In this case, SHELL_PLUS_PYGMENTS_ENABLED which adds some syntax
    # highlighting to the generated SQL.
    with monkey_patch_cursordebugwrapper(print_sql=True, confprefix="SHELL_PLUS", print_sql_location=False):
        # Pick a source but not execute the query.
        source_qs = inc_models.Source.objects.filter(name__iexact='sysco')

        print("Searching by starting from Item and specifying source.")
        qs = inc_models.Item.objects.available_items(source=source_qs)
        for item in qs:
            print(f"Item: {item}")

        print("\n" * 2)

        print("Searching by starting from Source - this returns items associated with the source.")
        source = source_qs.first()
        for item in source.items.available_items():
            print(f"Item: {item}")
