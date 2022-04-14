import itertools
import datetime
import json

from dateutil import relativedelta

from django import urls
from django.contrib.postgres import aggregates as pg_agg
from django.db import models
from django.db.models import base as models_base
from django.db.models import functions
from django.utils import timezone

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields
from .category import Category
from .department import Department
from .raw_item import RawItem
from .raw_state import RawState
from .source import Source
from . import mixins as inv_mixins


class RawIncomingItemManager(inv_mixins.GetsManagerMixin, sc_models.WideFilterManagerMixin, models.Manager):
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

    def calculate_order_values(self, order_qs):
        # Tack on next state so we don't have to make a separate query for it.  The orm doesn't like relations being
        # used in update statements.
        order_qs_annotated = order_qs.annotate(
            next_state_id=models.Case(
                models.When(
                    models.Q(state__next_state__name=models.Value('calculated')),
                    then=models.F('state__next_state_id')
                ),
                default=models.F('state_id'),
            ))
        # Group by that state since it should be the same for every record.
        sum_qs = order_qs_annotated.values('next_state_id').annotate(
            sum_total_packs=models.Sum('delivered_quantity'),
            sum_extended_price=models.Sum('extended_price')
        )
        # Should only return one record and will have the two totals and state id.  Tried .first() but the "LIMIT 1"
        # added to the query seemed to apply before the "GROUP BY" so the totals were broken.
        # Looking at the --print-sql output, the .first() caused .id to be added to GROUP and ORDER BY clauses meaning
        # the GROUP was pointless as each record became its own group.
        sums = sum_qs[0]
        # unit_quantity_calced=models.Case(
        #     models.When(models.F('unit_size'), then=models.F('')),
        #     default=models.Value(1)
        # )
        return order_qs.update(
            total_packs=sums['sum_total_packs'], total_price=sums['sum_extended_price'], state_id=sums['next_state_id'])

    def categories(self, limit_state=None, qs=None, only_new=False):
        return self._distinct_things('category', Category, limit_state=limit_state, qs=qs, only_new=only_new)

    def departments(self, limit_state=None, qs=None, only_new=False):
        return self._distinct_things('department', Department, limit_state=limit_state, qs=qs, only_new=only_new)

    def failed(self, method=None):
        qs = self.filter(state__failed=True)
        if method:
            qs = qs.filter(failure_reasons__icontains=f'"method": "{method}"')
        return qs

    def get_queryset(self):
        """
        Automatically includes the RawState model in orm queries.  Without it, referencing the state would cause a
        separate query for every record.
        """
        qs = super().get_queryset()
        qs = qs.select_related(
            'state', 'state__next_state', 'state__next_error_state', 'source_obj', 'category_obj', 'department_obj',
            'rawitem_obj')
        return qs

    # def __getattr__(self, item):
    #     ready_prefix = "ready_to_"
    #     if isinstance(item, str) and item.startswith(ready_prefix) and item != "ready_to_do_action":
    #         the_something = item[len(ready_prefix):]
    #         if the_something in RawState.ACTIONS_TO_STATES:
    #             return functools.partial(self.ready_to_do_action, the_something)
    #     raise AttributeError(item)

    def get_raw_item_filter(self, qs=None):
        qs = (qs or self)
        ri_filter = models.Q()
        distinct_qs = qs.order_by('source', 'name', 'unit_size', 'pack_quantity')
        distinct_qs = distinct_qs.distinct('source', 'name', 'unit_size', 'pack_quantity')
        for rii in distinct_qs:
            ri_filter |= rii.get_raw_item_filter()
        return ri_filter

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
        ready_qs = self.values('source', 'delivery_date', 'department', 'order_number').annotate(
            item_ids=pg_agg.ArrayAgg('id'),
            line_item_count=models.Count('id'),
            ready_to_calculate=models.Sum(
                models.Case(
                    models.When(state__next_state=RawState.objects.get_by_action('calculate'), then=1),
                    default=models.Value(0)
                )
            ),
            next_states=pg_agg.ArrayAgg(models.F('state__next_state__name'), distinct=True, ordering=['state__next_state__name']),
        ).filter(line_item_count=models.F('ready_to_calculate'))
        # ).filter(next_states__contains=['calculated'])
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
            print(f"{s['state__value']} {s['state__name']} = {s['count']}")

    def console_invalid_item_combos(self):
        short_list = ['source', 'name', 'unit_size', 'pack_quantity', ]
        for item in self.invalid_item_combos():
            item_key = "|".join([str(item[field]) for field in short_list])
            print(f"{item_key}\t{item['categories']}\t{item['item_codes']}")

    def console_routinely_ordered_items(self, months=3, selected_item_filter=None, sep=';'):
        """
        Output is tab-delimited and designed to be copied to a spreadsheet.
        item_code is prefixed with a single quote so leading zeros are not hidden.
        """
        squashed_data = self.routinely_ordered_items(months=months, selected_item_filter=selected_item_filter)
        start_date = sc_utils.get_monthly_date_range(months)[0]

        line = f"category{sep}common_name{sep}item_code{sep}name{sep}unit_size{sep}"
        line += f"{sep}".join(
            [(start_date + relativedelta.relativedelta(months=m)).strftime('%Y-%m') for m in range(months)])
        line += f"{sep}first_pack_price{sep}last_pack_price{sep}pct_change"
        print(line)
        for key in squashed_data.keys():
            line = f"{squashed_data[key]['category']}{sep}{squashed_data[key]['common_name']}{sep}"
            line += f"'{squashed_data[key]['item_code']}{sep}{squashed_data[key]['name']}"
            line += f"{sep}{squashed_data[key]['unit_size']}"
            for year_month in squashed_data[key]['dates'].keys():
                line += f"{sep}{squashed_data[key]['dates'][year_month]['max_pack_price']}"
            line += f"{sep}{squashed_data[key]['first_pack_price']}"
            line += f"{sep}{squashed_data[key]['last_pack_price']}"
            pct_change = (squashed_data[key]['last_pack_price'] / squashed_data[key]['first_pack_price'] - 1)
            line += f"{sep}{round(pct_change, 2)}"
            print(line)

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
        return self.values('state__value', 'state__name').annotate(count=models.Count('id'))

    def invalid_item_combos(self):
        # from do_clean, this looks for items which would cause dupes when including category/item_code.
        short_list = ['source', 'name', 'unit_size', 'pack_quantity', ]
        short_qs = self.values(*short_list).annotate(
            record_count=models.Count('id'),
            category_count=models.Count('category', distinct=True),
            item_code_count=models.Count('item_code', distinct=True),
            categories=pg_agg.ArrayAgg('category', distinct=True, ordering=['category']),
            item_codes=pg_agg.ArrayAgg('item_code', distinct=True, ordering=['item_code']),
        ).order_by(*short_list).filter(
            models.Q(category_count__gt=1) | models.Q(item_code_count__gt=1)
        )
        return short_qs

    def routinely_ordered_items(self, months=3, selected_item_filter=None):
        """
        Find items which have multiple orders over a given number of months.
        Want those orders to be spread vaguely evenly.
        Should those orders be roughly equal in quantity?
        """
        # Start a queryset that limits to the given months and excludes donations and out-of-stock items.
        date_range = sc_utils.get_monthly_date_range(months)
        root_qs = self.filter(delivery_date__range=date_range)
        root_qs = root_qs.exclude(models.Q(po_text='donation') | models.Q(delivered_quantity=0))
        # timedelta doesn't accept months so get the approx number of days and divide by two.
        required_gap = datetime.timedelta(days=months*30/2)

        if selected_item_filter is None:
            # The caller can supply their own set of items
            # Select items which have been ordered multiple times in the given months.
            selected_item_qs = root_qs.values('name', 'item_code').annotate(
                items=models.Count('id'),
                first_order=models.Min('delivery_date'),
                last_order=models.Max('delivery_date'),
            )
            selected_item_qs = selected_item_qs.filter(
                first_order__year=date_range[0].year, first_order__month=date_range[0].month,
                last_order__year=date_range[1].year, last_order__month=date_range[1].month
            )
            # selected_item_qs = selected_item_qs.exclude(
            #     models.Q(first_order__lte=models.F('last_order')-required_gap) | models.Q(items__lt=int(months/2))
            # )

            # Make the selected items into a filter.  Django ORM doesn't do multi-field joins automatically.
            selected_item_filter = models.Q()
            for si in selected_item_qs:
                selected_item_filter |= models.Q(name=si['name'], item_code=si['item_code'])

        # Filter the root queryset by the selected items
        filtered_qs = root_qs.filter(selected_item_filter)

        # Now do all the fun stuff to get the per-month numbers for the selected items.
        qs = filtered_qs.values(
            'category_obj__name',
            'rawitem_obj__common_item_name_group__name__name',
            'name', 'item_code', 'unit_size',
            year_month=functions.Concat(
                models.F('delivery_date__year'), models.Value('-'), functions.LPad(
                    functions.Cast(models.F('delivery_date__month'), models.CharField()), 2, models.Value('0')),
                output_field=models.CharField()
            )
        )
        qs = qs.annotate(
            items=models.Count('id'),
            # TODO: $/weight items won't work well with pack_price?  maybe?
            max_pack_price=models.Max('pack_price'),
            total_extended_price=models.Sum('extended_price'),
            total_delivered_quantity=models.Sum('delivered_quantity'),
        )

        qs = qs.order_by(
            'category_obj__name', 'rawitem_obj__common_item_name_group__name__name', 'name', 'item_code', 'unit_size',
            'year_month')
        return self.squash_data_routinely_ordered_items(qs, date_range[0], months)

    def squash_data_routinely_ordered_items(self, qs, start_date, months):
        squashed_data = {}
        for record in qs:
            key = f"{record['category_obj__name']}|{record['item_code']}|{record['name']}"
            if key not in squashed_data:
                # Set the item up with a complete zeroed set of months.
                squashed_data[key] = {
                    'category': record['category_obj__name'],
                    'common_name': record['rawitem_obj__common_item_name_group__name__name'],
                    'item_code': record['item_code'],
                    'name': record['name'],
                    'unit_size': record['unit_size'],
                    'dates': {
                        (start_date + relativedelta.relativedelta(months=m)).strftime('%Y-%m'): {
                            'max_pack_price': 0, 'total_extended_price': 0, 'total_delivered_price': 0,
                        }
                        for m in range(months)
                    },
                    'first_pack_price': 0, 'last_pack_price': 0,
                }
            # Overwrite the zeroed month with actual data.
            squashed_data[key]['dates'][record['year_month']]['max_pack_price'] = record['max_pack_price']
            squashed_data[key]['dates'][record['year_month']]['total_extended_price'] = record['total_extended_price']
            squashed_data[key]['dates'][record['year_month']]['total_delivered_quantity'] = record['total_delivered_quantity']
            if squashed_data[key]['first_pack_price'] == 0:
                squashed_data[key]['first_pack_price'] = record['max_pack_price']
            squashed_data[key]['last_pack_price'] = record['max_pack_price']

        # converts the year_month dicts to lists to make template traversal easier.
        for key, item_data in squashed_data.items():
            # This depends on python using ordereddict to keep the yyyy_mm in proper order.  Since they were all
            # created in order, no fancy ordering needs to be done here.
            item_data['monthly_data'] = [year_month_data for year_month_data in item_data['dates'].values()]
        return squashed_data


class RawIncomingItem(inv_mixins.GetsModelMixin, sc_models.WideFilterModelMixin, sc_models.DatedModel):
    """
    This is the line as it would be on a spreadsheet.  All information is included verbatim.  Any individual line item
    within an order should be able to tell you all the order information (duplication, yes).
    """
    wide_filter_fields = {
        'item_id': 'id',
        'name': [
            'name', 'rawitem_obj__name', 'rawitem_obj__better_name',
            'rawitem_obj__common_item_name_group__uncommon_item_names',
            'rawitem_obj__common_item_name_group__names__name'],
        'source': ['source', 'source_obj__name', 'source_obj_id'],
        'category': ['category', 'category_obj__name', 'category_obj_id'],
        'department': ['department', 'department_obj__name', 'department_obj_id'],
        'order_number': 'order_number',
        'po_text': 'po_text',
        'comment': ['order_comment', 'item_comment', 'rawitem_obj__item_comment'],
        'unit_size': ['unit_size', 'rawitem_obj__unit_size'],
        'quantity': ['pack_quantity', 'rawitem_obj__pack_quantity', 'ordered_quantity', 'delivered_quantity'],
        'code': ['item_code', 'extra_code', 'rawitem_obj__item_code', 'rawitem_obj__extra_code'],
    }
    wide_filter_fields_any = ['source', 'category', 'department']

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
    unit_quantity = models.IntegerField(default=1, help_text="For unit_size=ct/dz, this converts that to a number")
    total_weight = sc_fields.DecimalField()
    pack_quantity = sc_fields.DecimalField(default=1)
    pack_price = sc_fields.MoneyField()
    pack_tax = sc_fields.MoneyField()
    extended_price = sc_fields.MoneyField()

    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")
    scanned_image_filename = sc_fields.CharField(
        help_text="Filename of the scanned file.  Might have multiple per order.")

    state = models.ForeignKey(
        "inventory.RawState", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items",
        default=RawState.objects.initial_state
    )
    failure_reasons = models.TextField(null=True, blank=True)

    source_obj = models.ForeignKey(Source, on_delete=models.CASCADE, null=True)
    category_obj = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    department_obj = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
    rawitem_obj = models.ForeignKey(
        RawItem, on_delete=models.CASCADE, null=True, related_name="raw_incoming_items",
        related_query_name="raw_incoming_items")

    objects = RawIncomingItemManager()
    reports = RawIncomingItemReportManager()
    non_input_fields = ['state', 'failure_reasons', 'created', 'modified', 'id']

    class Meta:
        ordering = ("delivery_date", "source", "order_number", "line_item_position")

    def __str__(self):
        return f"{self.delivery_date}|{self.source}|{self.order_number}|{self.line_item_position}|{self.created}|{self.name}"

    def find_similar(self, by_field='name', include_default=False, exact_match=False):
        """
        Searches for other records with the same/similar specified field.  Does not exclude the current item.
        """
        value = getattr(self, by_field)
        default_value = None
        for f in self._meta.get_fields():
            if f.name == by_field:
                default_value = f.default
                break
        compare_func = 'iexact' if exact_match else 'icontains'
        if not include_default and (value == default_value):
            return self.__class__.objects.none()
        return self.__class__.objects.filter(**{f"{by_field}__{compare_func}": value})

    def get_absolute_url(self):
        return urls.reverse("inventory:rawincomingitem_detail", kwargs={'pk': self.id})

    def get_prices(self):
        # delivered_quantity = number of packs delivered
        # pack_quantity = number of units in a single pack
        # unit_quantity = for ct/dz, converts to the number of items in a unit (# of eggs - sysco comes in 30dz)
        # unit_size = pound, count, nothing, ounce.  How many/big is a single unit
        # pack_price = price of a single pack
        # pack_tax = total tax for the quantity delivered
        # extended_price = total price (with tax) for the quantity delivered
        # let price_per_unit = total_price / quantity / pack_quantity;
        if not self.delivered_quantity or not self.pack_quantity:
            return {
                "price_per_pack": 0.0,
                "price_per_unit": 0.0,
                "price_per_count": 0.0,
            }
        price_per_unit = self.extended_price / self.delivered_quantity / self.pack_quantity
        price_per_count = price_per_unit / self.unit_quantity
        # avg_pack_weight = None
        # avg_unit_weight = None
        pack_price = price_per_unit * self.pack_quantity  # NOTE: tax got included by using extended_price
        # if self.total_weight:
        #     avg_pack_weight = self.total_weight / self.delivered_quantity
        #     avg_unit_weight = avg_pack_weight / self.pack_quantity
        return {
            "price_per_pack": round(pack_price, 4),
            "price_per_unit": round(price_per_unit, 4),
            "price_per_count": round(price_per_count, 4),
        }

    def get_raw_item_filter(self):
        """
        Returns a filter that can be used to find this item in RawItem before the foreign key is set.
        """
        return models.Q(
            source__name=self.source, name=self.name, unit_size=self.unit_size, pack_quantity=self.pack_quantity)

    @property
    def has_in_stock(self):
        # Importing here to avoid circular references.  Hadn't tried with import at top.
        from .item_in_stock import ItemInStock
        _has_in_stock = False
        try:
            _has_in_stock = self.in_stock is not None
        except ItemInStock.DoesNotExist:
            pass
        return _has_in_stock
