from inventory import models as inv_models


def _do_calculate():
    """
    step 3
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_calculate()
    print(f"do_calculate found {qs.count()} records to calculate.")
    items_to_update = []
    for i, item in enumerate(qs):
        if i % 2 == 0:
            item.state = item.state.next_state
        else:
            item.state = item.state.next_error_state
        items_to_update.append(item)
    return items_to_update

