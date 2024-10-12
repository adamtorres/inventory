from django.db import models
from django.db.models import functions

from .. import models as inv_models


class DuplicateItems(object):
    @staticmethod
    def get_orders_queryset():
        return inv_models.SourceItem.objects.exclude(
            item_code__exact=''
        ).values('delivered_date', 'source', 'order_number').annotate(
                source_name=models.F('source__name'),
                count_line_item=models.Count('id'),
                count_distinct_line_item=models.Count('item_code', distinct=True),
            ).exclude(count_line_item=models.F('count_distinct_line_item'))

    @staticmethod
    def get_item_queryset(order):
        items_qs = inv_models.SourceItem.objects.annotate(
            created_date=functions.TruncDate('created')
        ).filter(
            delivered_date=order['delivered_date'], source=order['source'], order_number=order['order_number'])
        return items_qs.order_by('item_code', 'created')

    @staticmethod
    def run():
        orders_qs = DuplicateItems.get_orders_queryset()
        orders = {
            "order_count": orders_qs.count(),
            "orders": [],
        }
        for i, order in enumerate(orders_qs):
            order = {
                "delivered_date": order['delivered_date'],
                "source": order['source'],
                "source_name": order['source_name'],
                "order_number": order['order_number'],
                "line_items": [],
            }
            for item in DuplicateItems.get_item_queryset(order):
                order["line_items"].append(item)
            orders["orders"].append(order)
        return orders
