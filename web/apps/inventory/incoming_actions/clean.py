from django.db import models

from inventory import models as inv_models


def _do_clean():
    """
    step 1
    Purpose: Standardize dates, casing, numbers, whatever else makes sense.
    Result: either changes an item to 'cleaned' or 'failed_clean' state.
    """
    # TODO: Should 'clean' check for missing departments/categories/sources/etc?
    # TODO: What is the difference between clean and
    qs = inv_models.RawIncomingItem.objects.ready_to_clean()
    qs = qs[:1]
    print(f"do_clean found {qs.count()} records to clean.")
    items_to_update = []
    for i, item in enumerate(qs):
        print(item._meta.fields)
        failures = clean_item(item)
        if failures:
            item.state = item.state.next_error_state
        else:
            item.state = item.state.next_state
        items_to_update.append(item)
    return items_to_update


def clean_item(item):
    failures = []
    for field in item._meta.fields:
        if isinstance(field, (models.CharField, models.TextField)):
            if not clean_text_field(field):
                failures.append({'field': field.name, 'failure': 'clean_text_field'})

    return failures


def clean_text_field(field):
    return True
