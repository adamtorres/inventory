# From django_extensions/management/commands/shell_plus.py line 517
# with monkey_patch_cursordebugwrapper(
#         print_sql=options["print_sql"] or print_sql,
#         truncate=truncate,
#         print_sql_location=options["print_sql_location"],
#         confprefix="SHELL_PLUS"):
import datetime

from django.db import models
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from incoming import models as inc_models
from inventory import models as inv_models
import scrap


def test_available_items():
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


def test_empty_filter():
    qs = inc_models.Item.objects.filter(name='this should not return any objects.')
    if not qs:
        print("if not qs returned true.  This hopefully works.")
    else:
        print("if not qs returned false.  This would not be ideal.")


def test_consolidated_inventory():
    inv_dict = inv_models.Item.objects.get_categorized_inventory()
    for i in inv_dict:
        print(i)
    # for category, items in inv_dict.items():
    #     print(f"{category} has {len(items)} kinds of items")
    #     for item in items:
    #         print(f"{item}")


def test_location():
    for l in inv_models.Change.objects.summary_relative_by_month(12):
        print(l)


def test_incoming_item_group_listing():
    data = inc_models.IncomingItemGroup.objects.list_groups_by_converted_state()
    for k in data.keys():
        lines = []
        for i in data[k]:
            line = []
            line.append(f"{i.source_name.ljust(10)}")
            line.append(f"{i.converted_state.ljust(15)}")
            line.append(f"{i.descriptor.ljust(50)}")
            line.append(f"{str(i.total_price).rjust(10)}")
            line.append(f"{str(i.total_items).rjust(10)}")
            line.append(f"{str(i.total_packs).rjust(10)}")
            lines.append(" | ".join(line))
            # lines.append(f"{i.descriptor.ljust(50)} | {str(i.total_price).rjust(10)} | {str(i.total_packs).rjust(10)}")
        print(f"Key: {k}")
        print("\n".join(lines[:5]))
        print("... snip ...")
        print("\n".join(lines[-5:]))
        print()


def test_incoming_item_group_listing_values():
    data = inc_models.IncomingItemGroup.objects.list_groups(values=True)
    for i in data[:5]:
        print(i)


def test_date_math():
    def _date_math(m):
        print(f"months_ago({m}) = {scrap.relative_months(m)}")
        print("")
        for dow in ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']:
            print(f"months_ago({m}, first_dow='{dow}') = {scrap.relative_months(m, first_dow=dow)}")
        for dow in ['SU', 'MO', 'TU', 'WE', 'TH', 'FR', 'SA']:
            print(f"months_ago({m}, last_dow='{dow}') = {scrap.relative_months(m, last_dow=dow)}")
        print("")
        print(f"months_ago({m}, start_of_month=True) = {scrap.relative_months(m, start_of_month=True)}")
        print("")
        print(f"months_ago({m}, end_of_month=True) = {scrap.relative_months(m, end_of_month=True)}")

    dt = datetime.datetime.today()
    _date_math(dt)
    _date_math(0)


def update_action_date_from_bulk_load():
    # TODO: need a way to convert IIG to Change and then apply with action_date preserved.
    changes_to_update = []
    for i, c in enumerate(inv_models.Change.objects.exclude(action_date=models.F('incomingitemgroup__action_date'))):
        print(f"{c.action_date} | {c.source.action_date}")
        c.action_date = c.source.action_date
        changes_to_update.append(c)
    if changes_to_update:
        inv_models.Change.objects.bulk_update(changes_to_update, ['action_date'])
    # inv_models.Change.objects.all().update(action_date=models.F('incomingitemgroup__action_date'))


def run():
    print((("=" * 150) + "\n") * 3)
    # The configprefix is used to get some settings.  In this case, SHELL_PLUS_PYGMENTS_ENABLED which adds some syntax
    # highlighting to the generated SQL.
    with monkey_patch_cursordebugwrapper(print_sql=True, confprefix="SHELL_PLUS", print_sql_location=False):
        # update_action_date_from_bulk_load()
        test_incoming_item_group_listing()
