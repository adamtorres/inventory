import json

from django.utils import timezone
from django.db import models

from inventory import models as inv_models


def _do_clean(batch_size=0):
    """
    step 1
    Purpose: Standardize dates, casing, numbers, whatever else makes sense.
    Result: either changes an item to 'cleaned' or 'failed_clean' state.
    """
    # TODO: Should 'clean' check for missing departments/categories/sources/etc?
    qs = inv_models.RawIncomingItem.objects.ready_to_clean()
    if batch_size > 0:
        qs = qs[:batch_size]
    items_to_update = []
    fields_to_update = {'state'}
    cleaner = ItemCleaner()
    for i, item in enumerate(qs):
        fields_to_update.update(cleaner.clean(item))
        items_to_update.append(item)
        cleaner.reset()
    print(f"do_clean: items_to_update={len(items_to_update)}, fields_to_update={fields_to_update}")
    return items_to_update, fields_to_update


class ItemCleaner(object):
    failures = []
    updated_fields = set()
    now = None
    now_date = None
    item = None

    def __init__(self):
        self.now = timezone.now()
        self.now_date = self.now.date()

    def clean(self, item):
        self.item = item
        for field in item._meta.fields:
            # Skipping certain fields
            if field.name in item.non_input_fields:
                continue

            # Generic cleaning based on field type
            if isinstance(field, (models.CharField, models.TextField)):
                self.clean_text_field(field)
            if isinstance(field, (models.DateField, models.DateTimeField)):
                self.clean_date_field(field)

            # Clean specific fields if a cleaning method exists.
            clean_method_name = f"clean_{field.name}"
            if hasattr(self, clean_method_name) and callable(getattr(self, clean_method_name)):
                getattr(self, clean_method_name)()

        if self.failures:
            item.state = item.state.next_error_state
            item.failure_reasons = json.dumps(self.failures, sort_keys=True)
            self.updated_fields.update(['state', 'failure_reasons'])
        else:
            item.state = item.state.next_state
            self.updated_fields.add('state')
        return self.updated_fields

    def clean_date_field(self, field):
        value = getattr(self.item, field.name)
        # Currently, the only check I can think of is to make sure no dates are in the future.
        if not value:
            # Some dates can be None.
            return
        if value > (self.now if isinstance(field, models.DateTimeField) else self.now_date):
            self.failures.append({'field': field.name, 'method': 'clean_date_field', 'failure': 'date in future'})

    def clean_name(self):
        if not self.item.name:
            self.failures.append({'field': 'name', 'method': 'clean_name', 'failure': 'empty or None'})

    def clean_text_field(self, field):
        value = getattr(self.item, field.name)
        if value == "some generic text failure":
            self.failures.append({'field': field.name, 'method': 'clean_text_field', 'failure': '?'})
        if value != value.strip():
            setattr(self.item, field.name, value.strip())
            self.updated_fields.add(field.name)

    def reset(self):
        self.failures.clear()
        self.updated_fields.clear()
        self.item = None
