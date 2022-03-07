from inventory import models as inv_models


def _do_clean():
    """
    step 1
    Purpose: Standardize dates, casing, numbers, whatever else makes sense.
    Result: either changes an item to 'cleaned' or 'failed_clean' state.
    """
    # TODO: Should 'clean' check for missing departments/categories/sources/etc?
    qs = inv_models.RawIncomingItem.objects.ready_to_clean()
    print(f"do_clean found {qs.count()} records to clean.")
    items_to_update = []
    for i, item in enumerate(qs):
        if i % 2 == 0:
            item.state = item.state.next_state
        else:
            item.state = item.state.next_error_state
        items_to_update.append(item)
    return items_to_update
