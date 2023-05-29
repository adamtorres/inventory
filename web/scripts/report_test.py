from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from inventory import models as inv_models, reports as inv_reports


def graph_data():
    # 30dz eggs from sysco
    qs = inv_models.SourceItem.objects.wide_filter([('item_code', ('2105773',)), ('source', ('sysco',))])
    qs = qs.order_by().order_by('delivered_date', 'source_id', 'order_number', 'line_item_number')
    data = {'delivered_date': [], 'per_use_cost': [], 'initial_quantity': []}
    # previous_date = None
    for si in qs:
        # if not previous_date:
        #     previous_date = si.delivered_date
        data['delivered_date'].append(si.delivered_date)
        data['per_use_cost'].append(si.per_use_cost())
        data['initial_quantity'].append(si.initial_quantity())
    first_date = data['delivered_date'][0]
    last_date = data['delivered_date'][-1]
    print(f"First date: {first_date}")
    print(f"Last date: {last_date}")


def run():
    with monkey_patch_cursordebugwrapper(print_sql=True, confprefix="SHELL_PLUS", print_sql_location=False):
        # inv_reports.SourceItemNamesAndQuantities.get_groupings()
        graph_data()

