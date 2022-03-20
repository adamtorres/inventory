import json
from django.db import models

from .. import models as inv_models


def _do_calculate(batch_size=1):
    """
    step 3
    """
    if batch_size <= 0:
        return [], set()
    # next_state = inv_models.RawState.objects.get_by_action('calculate')
    for order_qs in inv_models.RawIncomingItem.objects.ready_to_calculate():
        # print("=" * 120)
        inv_models.RawIncomingItem.objects.calculate_order_values(order_qs)
        # for item in order_qs:
        #     print(f"item = {item.delivered_quantity} / {item.total_packs} / {item.extended_price} / {item.total_price}")
        # print(
        #     f"source = {order['source']}, department = {order['department']}, order_number = {order['order_number']}, "
        #     f"line_item_count = {order['line_item_count']}")
        batch_size -= 1
        if batch_size <= 0:
            break

    # if batch_size > 0:
    #     qs = qs[:batch_size]
    items_to_update = []
    fields_to_update = {}
    return items_to_update, fields_to_update
