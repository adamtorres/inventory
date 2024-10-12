from django.db import models
from django.db.models import functions
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from inventory import models as inv_models

show_dupes_sql = """
select date_trunc('day', created) as day, count(1)
from inventory_sourceitem
where order_number = '585127305'
group by day
order by day;
"""

delete_sql = """
delete from inventory_sourceitem
where order_number = '585127305' and date_trunc('day', created) = '2023-09-09';
"""

find_duplicate_orders_sql = """
SELECT DATE_TRUNC('day', created) AS day, COUNT(1)
FROM inventory_sourceitem inv_si
JOIN inventory_source inv_s
ON inv_si.source_id = inv_s.id
GROUP BY day, order_number, inv_s.name
"""


def print_order(order):
    print(order)
    qs = inv_models.SourceItem.objects.annotate(created_date=functions.TruncDate('created')).filter(
        delivered_date=order['delivered_date'], source=order['source'], order_number=order['order_number'])
    qs = qs.order_by('item_code', 'created')
    for item in qs:
        print(f"\t{item.line_item_number} | {item.item_code} | {item.cryptic_name} | {item.created_date}")


def test_query():
    qs = inv_models.SourceItem.objects.exclude(
        item_code__exact=''
    ).values('delivered_date', 'source', 'order_number').annotate(
            count_line_item=models.Count('id'),
            count_distinct_line_item=models.Count('item_code', distinct=True),
        ).exclude(count_line_item=models.F('count_distinct_line_item'))
    print(f"item count mismatch: {qs.count()}")
    for i, order in enumerate(qs):
        print_order(order)
        if i >= 20:
            break


def test_query_concat():
    qs = inv_models.SourceItem.objects.annotate(
            order_id=functions.Concat(
                models.F('delivered_date'), models.Value('|'), models.F('source'), models.Value('|'), models.F('order_number'),
                output_field=models.CharField())
        ).values('order_id').annotate(
            count_line_item=models.Count('id'),
            count_distinct_line_item=models.Count('item_code', distinct=True),
        ).exclude(count_line_item=models.F('count_distinct_line_item'))
    print(f"item count mismatch: {qs.count()}")
    for i, order in enumerate(qs):
        print(order)
        if i >= 20:
            break


def run():
    with monkey_patch_cursordebugwrapper(print_sql=False, confprefix="SHELL_PLUS", print_sql_location=False):
        test_query()
