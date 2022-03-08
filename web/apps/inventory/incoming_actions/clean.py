import json

from django.utils import timezone
from django.db import models

from inventory import models as inv_models
from scrap import utils


def _do_clean(batch_size=0):
    """
    step 1
    Purpose: Standardize dates, casing, numbers, whatever else makes sense.
    Result: either changes an item to 'cleaned' or 'failed_clean' state.
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_clean()
    if batch_size > 0:
        qs = qs[:batch_size]
    items_to_update = []
    fields_to_update = {'state'}
    cleaner = ItemCleaner()
    for i, item in enumerate(qs):
        fields_to_update.update(cleaner.clean(item))
        items_to_update.append(item)
        cleaner.clear()
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

        validation_functions = [x for x in dir(self) if x.startswith("validate_") and callable(getattr(self, x))]
        for validation_func in validation_functions:
            getattr(self, validation_func)()

        if self.failures:
            item.state = item.state.next_error_state
            print(self.failures)
            item.failure_reasons = json.dumps(self.failures, sort_keys=True, default=str)
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
            self.failures.append({
                'fields': [field.name], 'method': utils.get_function_name(), 'failure': 'date in future'})

    def clean_text_field(self, field):
        value = getattr(self.item, field.name)
        if value == "some generic text failure":
            self.failures.append({'fields': [field.name], 'method': utils.get_function_name(), 'failure': '?'})
        if value != value.strip():
            setattr(self.item, field.name, value.strip())
            self.updated_fields.add(field.name)

    def clear(self):
        """
        Reset ItemCleaner to be ready to clean another item.
        """
        self.failures.clear()
        self.updated_fields.clear()
        self.item = None

    def validate_category(self):
        if not self.item.category:
            self.failures.append({
                'fields': ['category'], 'method': utils.get_function_name(), 'failure': 'empty or None'})

    def validate_delivery_and_order_dates(self):
        """
        The delivery must not happen before the order.
        """
        if self.item.order_date and self.item.delivery_date < self.item.order_date:
            self.failures.append({
                'fields': ['order_date', 'delivery_date'], 'method': utils.get_function_name(),
                'failure': 'delivery_date is earlier than order_date'})

    def validate_department(self):
        if not self.item.department:
            self.failures.append({
                'fields': ['department'], 'method': utils.get_function_name(), 'failure': 'empty or None'})

    def validate_name(self):
        if not self.item.name:
            self.failures.append({'fields': ['name'], 'method': utils.get_function_name(), 'failure': 'empty or None'})

    def validate_quantity_and_prices(self):
        """
        If an item is delivered, we should have prices
        """
        if self.item.delivered_quantity and not self.item.pack_price:
            self.failures.append({
                'fields': ['delivered_quantity', 'pack_price'], 'method': utils.get_function_name(),
                'failure': 'delivered_quantity > 0 but pack_price is 0'})

        if self.item.total_weight and self.item.extended_price:
            difference = (self.item.total_weight * self.item.pack_price) - self.item.extended_price
            if abs(difference) > 1.0:
                # Many weight calculations are not very accurate.  Assumption is the amounts on the invoice have been
                # rounded which make the recalculations off by less than $1.  most are less than $0.17.
                self.failures.append({
                    'fields': ['total_weight', 'pack_price', 'extended_price'], 'method': utils.get_function_name(),
                    'failure': 'total_weight * pack_price != extended_price', 'difference': difference,
                })
        if not self.item.total_weight and self.item.extended_price:
            if self.item.delivered_quantity * self.item.pack_price != self.item.extended_price:
                self.failures.append({
                    'fields': ['ordered_quantity', 'delivered_quantity', 'pack_price', 'extended_price'],
                    'method': utils.get_function_name(),
                    'failure': 'delivered_quantity * pack_price != extended_price',
                    'difference': (self.item.delivered_quantity * self.item.pack_price) - self.item.extended_price
                })
