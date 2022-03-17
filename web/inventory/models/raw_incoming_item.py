import functools
import itertools

from django import urls
from django.contrib.postgres import aggregates as pg_agg
from django.db import models
from django.db.models import base as models_base
from django.db.models import functions

from scrap import models as sc_models, fields as sc_fields
from .category import Category
from .department import Department
from .raw_item import RawItem
from .raw_state import RawState
from .source import Source


class RawIncomingItemManager(sc_models.WideFilterManagerMixin, models.Manager):
    def _limit_state(self, qs, limit_state):
        """
        Used by a variety of querysets to limit by RawState in a flexible manner.

        limit_state can be a single RawState, a Queryset returning RawState(s), or a custom Q filter.
        """
        if isinstance(limit_state, RawState):
            qs = qs.filter(state=limit_state)
        if isinstance(limit_state, models.QuerySet):
            qs = qs.filter(state__in=limit_state)
        if isinstance(limit_state, models.Q):
            qs = qs.filter(limit_state)
        return qs

    def _distinct_things(self, field, thing, limit_state=None, qs=None, only_new=False):
        """
        field = a field name in the set to be filtered - 'source', 'category', etc
        thing = model of the filtered name - Source, Category, etc
        """
        # TODO: should this be expanded to handle multiple fields?  RawItem uses 4 fields.
        qs = (qs or self).values(field).distinct(field)
        qs = self._limit_state(qs, limit_state)
        if only_new and isinstance(thing, models_base.ModelBase):
            filter_kwarg = {f"{field}__in": thing.objects.all().values_list('name', flat=True)}
            qs = qs.exclude(**filter_kwarg)
        return qs.order_by(field)

    def categories(self, limit_state=None, qs=None, only_new=False):
        return self._distinct_things('category', Category, limit_state=limit_state, qs=qs, only_new=only_new)

    def departments(self, limit_state=None, qs=None, only_new=False):
        return self._distinct_things('department', Department, limit_state=limit_state, qs=qs, only_new=only_new)

    def get_queryset(self):
        """
        Automatically includes the RawState model in orm queries.  Without it, referencing the state would cause a
        separate query for every record.
        """
        qs = super().get_queryset()
        qs = qs.select_related('state', 'state__next_state', 'state__next_error_state')
        # qs = qs.prefetch_related('state', 'state__next_state', 'state__next_error_state')
        return qs

    # def __getattr__(self, item):
    #     ready_prefix = "ready_to_"
    #     if isinstance(item, str) and item.startswith(ready_prefix) and item != "ready_to_do_action":
    #         the_something = item[len(ready_prefix):]
    #         if the_something in RawState.ACTIONS_TO_STATES:
    #             return functools.partial(self.ready_to_do_action, the_something)
    #     raise AttributeError(item)

    def failed(self, method=None):
        qs = self.filter(state__failed=True)
        if method:
            qs = qs.filter(failure_reasons__icontains=f'"method": "{method}"')
        return qs

    def items(self, limit_state=None, qs=None, only_new=False):
        fields = ['source_obj', 'name', 'unit_size', 'pack_quantity', 'category_obj', 'item_code']
        qs = (qs or self).values(*fields)
        qs = qs.distinct(*fields)
        qs = self._limit_state(qs, limit_state)
        if only_new:
            qs = qs.exclude(rawitem_obj__isnull=False)
        qs = qs.order_by(*fields)
        source_cache = {obj.id: obj for obj in Source.objects.all()}
        category_cache = {obj.id: obj for obj in Category.objects.all()}
        qs_list = []
        for item in qs:
            qs_list.append({
                "source": source_cache[item["source_obj"]],
                "category": category_cache[item["category_obj"]],
                "name": item["name"],
                "unit_size": item["unit_size"],
                "pack_quantity": item["pack_quantity"],
                "item_code": item["item_code"],
            })
        return qs_list

    def make_example_changes(self):
        self.filter(name__icontains="x").update(
            name=functions.Concat(models.Value('  '), models.F('name'), models.Value('  ')))

    def make_example_states(self):
        """
        Set states for records such that the distribution increases as the state.value increases.
        """
        states = itertools.cycle(RawState.objects.all().order_by('value'))
        items_to_update = []
        state = next(states)
        i = 0  # item counter per state
        for item in self.all():
            item.state = state
            i += 1
            if i >= state.value:
                # when the number of items in the current state equals/exceeds the current state.value, next state.
                state = next(states)
                i = 0
            items_to_update.append(item)
            if len(items_to_update) >= 100:
                self.bulk_update(items_to_update, fields=('state', ))
                items_to_update.clear()
        if items_to_update:
            self.bulk_update(items_to_update, fields=('state',))

    def orders(self, item_id=None):
        qs = self.values(
            'source', 'department', 'customer_number', 'order_number', 'po_text', 'order_comment', 'order_date',
            'delivery_date', 'total_price', 'total_packs')
        qs = qs.annotate(
            item_count=models.Count('id'),
            item_ids=pg_agg.ArrayAgg('id'),
        )
        qs = qs.order_by('delivery_date', 'source', 'order_number', )

        if item_id:
            item = self.get(id=item_id)
            qs = qs.filter(
                models.Q(delivery_date=item.delivery_date, source=item.source, order_number=item.order_number))

        return qs

    def ready_to_calculate(self):
        """
        step 2ish
        returns a queryset per iteration which includes the item records for a given order.
        """
        orders_qs = self.ready_to_calculate_orders()
        for order in orders_qs:
            yield self.filter(id__in=order['item_ids'])
        return

    def ready_to_calculate_orders(self):
        """
        step 2 - calculate total for orders.  This needs all items within an order to be ready to calculate.
        This does not return item records.  Returns one record per order which includes a list of item ids.
        """
        ready_qs = self.values('source', 'department', 'order_number').annotate(
            item_ids=pg_agg.ArrayAgg('id'),
            line_item_count=models.Count('id'),
            ready_to_calculate=models.Sum(
                models.Case(
                    models.When(state__next_state=RawState.objects.get_by_action('calculate'), then=1),
                    default=models.Value(0)
                )
            )
        ).filter(line_item_count=models.F('ready_to_calculate'))
        return ready_qs

    def ready_to_clean(self):
        """
        step 1 - fix various issues like extra whitespace around values
        cleaning does not require all items in an order to be ready.
        """
        return self.filter(state__next_state=RawState.objects.get_by_action('clean'))

    def ready_to_create(self):
        """
        step 3 - create supporting objects (category/department/source)
        """
        return self.filter(state__next_state=RawState.objects.get_by_action('create'))

    def ready_to_import(self):
        """
        step 4 - final step
        """
        return self.filter(state__next_state=RawState.objects.get_by_action('import'))

    def ready_to_do_action(self, action, *args):
        state_name = RawState.action_to_state_name(action)
        return self.filter(state__next_state__name=state_name)

    def reset_all(self):
        self.all().update(
            state=RawState.objects.get(value=0), failure_reasons=None,
            source_obj=None, category_obj=None, department_obj=None)

    def sources(self, limit_state=None, qs=None, only_new=False):
        """
        limit_state can be a single RawState, a Queryset returning RawState(s), or a custom Q filter.

        To get sources from records that are ready to create such and not dig through the entire table,
        RawIncomingItem.objects.sources(qs=RawIncomingItem.objects.ready_to_create())
        """
        return self._distinct_things('source', Source, limit_state=limit_state, qs=qs, only_new=only_new)


class RawIncomingItemReportManager(models.Manager):
    def console_count_by_action(self, action='clean'):
        print("state | not yet | ready | already there | beyond")
        for s in self.count_by_action(action).order_by('state'):
            print(
                f"{str(s['state']).rjust(5)} | {str(s['not_yet']).rjust(7)} | {str(s['ready']).rjust(5)} | "
                f"{str(s['already_there']).rjust(13)} | {str(s['beyond']).rjust(6)}")

    def console_group_by_current_state(self):
        for s in self.group_by_current_state().order_by('state'):
            print(f"{s['state']} {s['state__name']} = {s['count']}")

    def count_by_action(self, action="clean"):
        rs = RawState.objects.get(name=RawState.action_to_state_name(action))
        return RawIncomingItem.objects.values('state').annotate(
            not_yet=models.Sum(models.Case(
                models.When(state__next_state__value__lt=rs.value, then=models.Value(1)),
                default=models.Value(0))
            ),
            ready=models.Sum(models.Case(
                models.When(state__next_state=rs, then=models.Value(1)),
                default=models.Value(0))
            ),
            already_there=models.Sum(models.Case(
                models.When(state=rs, then=models.Value(1)),
                default=models.Value(0))
            ),
            beyond=models.Sum(models.Case(
                models.When(state__value__gt=rs.value, then=models.Value(1)),
                default=models.Value(0))
            ),
        )

    def group_by_current_state(self):
        return self.values('state', 'state__name').annotate(count=models.Count('id'))


class RawIncomingItem(sc_models.WideFilterModelMixin, sc_models.DatedModel):
    """
    This is the line as it would be on a spreadsheet.  All information is included verbatim.  Any individual line item
    within an order should be able to tell you all the order information (duplication, yes).
    """
    wide_filter_fields = {
        'name': [
            'name', 'rawitem_obj__name', 'rawitem_obj__better_name',
            'rawitem_obj__common_item_name_group__uncommon_item_names',
            'rawitem_obj__common_item_name_group__names__name'],
        'category': ['category_obj__name'],
    }

    # Order info - duplicated for all line items within an order
    source = sc_fields.CharField(help_text="source name")
    department = sc_fields.CharField(help_text="department name")
    customer_number = sc_fields.CharField()
    order_number = sc_fields.CharField(
        help_text="possibly unique text - some sources repeat or slightly modify this for back-ordered items")
    po_text = sc_fields.CharField(help_text="optional text on the invoice")
    order_comment = sc_fields.CharField(help_text="Anything noteworthy about this order")
    order_date = models.DateField(null=True, blank=True, help_text="When the order was placed.")
    delivery_date = models.DateField(help_text="When did we get the items.  Not when the items were shipped.")
    total_price = sc_fields.MoneyField()
    total_packs = sc_fields.DecimalField()

    # Line item info - specific to this one item within an order.
    line_item_position = models.PositiveSmallIntegerField("Position", null=True)

    category = sc_fields.CharField(blank=False, help_text="meat, dairy, produce, etc.")
    name = sc_fields.CharField(blank=False)
    # better_name = sc_fields.CharField(help_text="Less cryptic item name")

    # Won't have this for OUT items for Sysco orders as the invoice just shows "OUT" for the quantity.
    ordered_quantity = sc_fields.DecimalField()
    # delivered = accepted.  Does not include damaged/rejected items.
    delivered_quantity = sc_fields.DecimalField()

    item_code = sc_fields.CharField()
    extra_code = sc_fields.CharField()
    unit_size = sc_fields.CharField()
    total_weight = sc_fields.DecimalField()
    pack_quantity = sc_fields.DecimalField()
    pack_price = sc_fields.MoneyField()
    pack_tax = sc_fields.MoneyField()
    extended_price = sc_fields.MoneyField()

    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")
    scanned_image_filename = sc_fields.CharField(
        help_text="Filename of the scanned file.  Might have multiple per order.")

    state = models.ForeignKey(
        "inventory.RawState", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items",
        to_field="value", default=0
    )
    failure_reasons = models.TextField(null=True, blank=True)

    objects = RawIncomingItemManager()
    reports = RawIncomingItemReportManager()
    non_input_fields = ['state', 'failure_reasons', 'created', 'modified', 'id']

    source_obj = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)
    category_obj = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    department_obj = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    rawitem_obj = models.ForeignKey(RawItem, on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ("delivery_date", "source", "order_number", "line_item_position")

    def __str__(self):
        return f"{self.delivery_date}|{self.source}|{self.order_number}|{self.line_item_position}|{self.created}"

    def find_similar(self, by_field='name', include_default=False):
        value = getattr(self, by_field)
        default_value = None
        for f in self._meta.get_fields():
            if f.name == by_field:
                default_value = f.default
                break
        if not include_default and (value == default_value):
            return self.__class__.objects.none()
        return self.__class__.objects.filter(**{f"{by_field}__iexact": value})

    def get_absolute_url(self):
        return urls.reverse("inventory:rawincomingitem_detail", kwargs={'pk': self.id})
