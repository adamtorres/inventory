import json
from django.db import models

from inventory import models as inv_models


def _do_calculate(batch_size=1):
    """
    step 3
    """
    if batch_size <= 0:
        return [], set()
    for order_qs in inv_models.RawIncomingItem.objects.ready_to_calculate():
        print("=" * 120)
        next_state = inv_models.RawState.objects.get_by_action('calculate').next_state
        sums = order_qs.aggregate(
            sum_total_packs=models.Sum('delivered_quantity'),
            sum_extended_price=models.Sum('extended_price'),
        )
        order_qs.update(total_packs=sums['sum_total_packs'], total_price=sums['sum_extended_price'], state=next_state)
        for item in order_qs:
            print(f"item = {item.delivered_quantity} / {item.total_packs} / {item.extended_price} / {item.total_price}")
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
