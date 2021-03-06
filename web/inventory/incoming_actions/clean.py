import collections
import json
import re

from django.utils import timezone
from django.db import models

from .. import models as inv_models
from scrap import utils


UNIT_SIZE_COUNT_RE = re.compile(r"^(?P<value>\d+)(?P<unit>dz|ct)$", re.IGNORECASE)
UNIT_SIZE_POUND_RE = re.compile(r"^(?P<value>\d+)(?P<unit>lb)$", re.IGNORECASE)


def generate_existing_unit_pattern() -> str:
    r"^(?P<value>\d+)(?P<unit>dz|ct)$"
    existing_units = [u for u in inv_models.RawItem.objects.get_possible_unit_counts().keys() if u]
    if not existing_units:
        # Some defaults for when the database is new.
        existing_units = ["ct", "dz", "g", "gal", "in", "lb", "oz", "pt", "qt"]
    valid_unit_pattern = r"^(?P<value>\d+(\.\d+)?)(?P<unit>" + "|".join(existing_units) + ")$"
    return valid_unit_pattern


EXISTING_UNIT_SIZE_RE = re.compile(generate_existing_unit_pattern(), re.IGNORECASE)


def _do_clean(batch_size=0, allow_new_units=False):
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
    cleaner = ItemCleaner(allow_new_units=allow_new_units)
    for i, item in enumerate(qs):
        fields_to_update.update(cleaner.clean(item))
        items_to_update.append(item)
        cleaner.clear()
    problem_items = validate_item_combos(qs)

    # intersection returns items from the right when they match items from the left.
    # Use that to pick out the problem items and combine with existing failure_reasons.
    items_to_add_to_failure_reasons = list(set(problem_items).intersection(items_to_update))
    for item in items_to_add_to_failure_reasons:
        problem_item = problem_items.pop(problem_items.index(item))
        failure_reasons = []
        if item.failure_reasons:
            failure_reasons.extend(json.loads(item.failure_reasons))
        failure_reasons.extend(json.loads(problem_item.failure_reasons))
        item.failure_reasons = json.dumps(failure_reasons, sort_keys=True, default=str)
        item.state = problem_item.state

    print(f"do_clean: items_to_update={len(items_to_update)}, fields_to_update={fields_to_update}")
    return items_to_update, fields_to_update


class ItemCleaner(object):
    allow_new_units = False
    failures = []
    updated_fields = set()
    now = None
    now_date = None
    item = None

    def __init__(self, allow_new_units=False):
        self.now = timezone.now()
        self.now_date = self.now.date()
        self.allow_new_units = allow_new_units

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
        if self.item.po_text == "donation":
            # Donations don't have prices so none of these checks would pass.
            return
        if self.item.delivered_quantity and not self.item.pack_price:
            # Donations would fail here as no cost is applied.
            self.failures.append({
                'fields': ['delivered_quantity', 'pack_price'], 'method': utils.get_function_name(),
                'failure': 'delivered_quantity > 0 but pack_price is 0'})

        if self.item.total_weight and self.item.extended_price:
            difference = (self.item.total_weight * self.item.pack_price + self.item.pack_tax) - self.item.extended_price
            if abs(difference) > 1.0:
                # Many weight calculations are not very accurate.  Assumption is the amounts on the invoice have been
                # rounded which make the recalculations off by less than $1.  most are less than $0.17.
                self.failures.append({
                    'fields': ['total_weight', 'pack_price', 'extended_price'], 'method': utils.get_function_name(),
                    'failure': 'total_weight * pack_price + pack_tax != extended_price', 'difference': difference,
                })
        if not self.item.total_weight and self.item.extended_price:
            if (self.item.delivered_quantity * self.item.pack_price + self.item.pack_tax) != self.item.extended_price:
                self.failures.append({
                    'fields': ['ordered_quantity', 'delivered_quantity', 'pack_price', 'extended_price'],
                    'method': utils.get_function_name(),
                    'failure': 'delivered_quantity * pack_price + pack_tax != extended_price',
                    'difference': (self.item.delivered_quantity * self.item.pack_price) - self.item.extended_price
                })

    def validate_unit_size(self):
        """
        for any which end in "dz"(dozen) or "ct"(count), verify only numbers precede it.
        """
        if not self.item.unit_size:
            # Blank is fine but leaves nothing to check so no need to do anything else here.
            return
        check_existing = EXISTING_UNIT_SIZE_RE.match(self.item.unit_size)
        if not check_existing and not self.allow_new_units:
            self.failures.append({
                'fields': ['unit_size'],
                'method': utils.get_function_name(),
                'failure': 'unit_size does not appear to have a known unit size.',
            })
            return
        check_count = UNIT_SIZE_COUNT_RE.match(self.item.unit_size)
        if check_count:
            # looks like a simple count-based unit_size, adjust (field).
            unit_quantity = int(check_count.group('value'))
            if check_count.group('unit') == 'dz':
                unit_quantity *= 12
            self.item.unit_quantity = unit_quantity
            self.updated_fields.add('unit_quantity')
        check_pound = UNIT_SIZE_POUND_RE.match(self.item.unit_size)
        if not self.item.total_weight and check_pound:
            # Item's unit_size is in lb but there isn't a total_weight.
            unit_quantity = int(check_pound.group('value'))
            self.item.unit_quantity = unit_quantity
            self.updated_fields.add('unit_quantity')


def validate_item_combos(qs):
    """
    This needs to see a lot of records as it needs to check if the combination of fields that make up an item differs
    in fields outside source/name/unit_size/pack_quantity.  This is because the creation method currently uses distinct
    on all of those fields plus category, item_code, and extra_code.
    """
    print("do_clean:validate_item_combos")
    short_list = ['source', 'name', 'unit_size', 'pack_quantity']
    long_list = ['source', 'name', 'unit_size', 'pack_quantity', 'category', 'item_code',]
    # long_count = qs.distinct(*long_list).count()
    # short_count = qs.distinct(*short_list).count()
    # if long_count == short_count:
    #     return
    # qs.values(*short_list).annotate(count=models.Count('id'))
    long_qs = qs.values(*long_list).annotate(count=models.Count('id')).order_by(*long_list)
    item_count = collections.defaultdict(int)
    problems = set()
    for item in long_qs:
        item_key = f"{item['source']}|{item['name']}|{item['unit_size']}|{item['pack_quantity']}"
        item_count[item_key] += 1
        if item_count[item_key] > 1:
            problems.add(item_key)
    # if len(item_count) != short_count:
    #     print(f"!!! len(item_count)/{len(item_count)} != short_count/{short_count}")
    problem_items = []
    if not problems:
        # print(f"no problems?  then why didn't long_count/{long_count} == short_count/{short_count}?")
        print("no problems?")
    else:
        print(f"len(problems) = {len(problems)}")
        problem_filter = models.Q()
        for item_key in problems:
            key_bits = item_key.split('|')
            problem_filter = problem_filter | models.Q(
                source=key_bits[0], name=key_bits[1], unit_size=key_bits[2], pack_quantity=key_bits[3])
        failed_items = inv_models.RawIncomingItem.objects.filter(problem_filter)
        for item in failed_items:
            item.state = item.state.next_error_state
            item.failure_reasons = json.dumps([{
                'fields': ['source', 'name', 'unit_size', 'pack_quantity'], 'method': utils.get_function_name(),
                'failure': 'item combo dupes when including category/item_code/extra_code'}],
                sort_keys=True, default=str)
            problem_items.append(item)
    return problem_items


def console_report_on_failed_validate_item_combos():
    qs = inv_models.RawIncomingItem.objects.failed(method='validate_item_combos')
    qs = qs.order_by('source', 'name', 'unit_size', 'pack_quantity', 'category', 'item_code', 'extra_code')
    fields = [
        ('id', 'rjust'), ('source', 'ljust'), ('name', 'ljust'), ('unit_size', 'rjust'), ('pack_quantity', 'rjust'),
        ('category', 'ljust'), ('item_code', 'rjust'), ('extra_code', 'rjust')]
    max_len = {k[0]: 0 for k in fields}
    for item in qs:
        for k in fields:
            if max_len[k[0]] < len(str(getattr(item, k[0]))):
                max_len[k[0]] = len(str(getattr(item, k[0])))

    for item in qs:
        line = ""
        for k in fields:
            if line:
                line += " | "
            value = str(getattr(item, k[0]))
            just_func = getattr(value, k[1])
            line += f"{just_func(max_len[k[0]])}"
        print(line)
