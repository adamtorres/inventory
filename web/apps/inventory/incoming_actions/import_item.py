from inventory import models as inv_models


def _do_import(batch_size=1):
    """
    step 5
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_import()
    if batch_size > 0:
        qs = qs[:batch_size]
    print(f"do_import found {qs.count()} records to import.")
    items_to_update = []
    fields_to_update = {'state'}
    for i, item in enumerate(qs):
        if i % 2 == 0:
            item.state = item.state.next_state
        else:
            item.state = item.state.next_error_state
        items_to_update.append(item)
    return items_to_update, fields_to_update
