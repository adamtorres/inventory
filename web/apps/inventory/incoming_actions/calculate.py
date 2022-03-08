import json

from inventory import models as inv_models


def _do_calculate(batch_size=1):
    """
    step 3
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_calculate()
    if batch_size > 0:
        qs = qs[:batch_size]
    print(f"do_calculate found {qs.count()} records to calculate.")
    items_to_update = []
    fields_to_update = {'state'}
    for i, item in enumerate(qs):
        failures = []

        if not item.extended_price:
            if item.total_weight:
                # pack_price is the price per weight of all items.
                item.extended_price = item.total_weight * item.pack_price
            else:
                item.extended_price = item.delivered_quantity * item.pack_price
        else:
            # TODO: Should this validate the existing price?  Or should that be done in the 'clean' step?
            pass

        if failures:
            item.state = item.state.next_error_state
            item.failure_reasons = json.dumps(failures, sort_keys=True)
            fields_to_update.add('failure_reasons')
        else:
            item.state = item.state.next_state

        items_to_update.append(item)
    print(f"do_calculate: items_to_update={len(items_to_update)}, fields_to_update={fields_to_update}")
    return items_to_update, fields_to_update
