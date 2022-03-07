from inventory import models as inv_models


def _do_create():
    """
    step 4
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_create()
    print(f"do_create found {qs.count()} records to create.")
    items_to_update = []
    for i, item in enumerate(qs):
        if i % 2 == 0:
            item.state = item.state.next_state
        else:
            item.state = item.state.next_error_state
        items_to_update.append(item)
    return items_to_update

