from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid

from .incoming_item_group import IncomingItemGroup
from .item import Item
from scrap import models as sc_models


class IncomingItemManager(models.Manager, sc_models.FilterMixin):
    fields_to_filter_with_terms = [
        "item__name", "item__better_name",
        "item__common_item__name", "item__common_item__other_names__name"]
    filter_prefetch = ['item', 'item__common_item', 'parent']
    filter_order = ['item__common_item__name', 'parent__action_date']

    def cost_by_month(self, start_date=None, end_date=None):
        """
        A quick totaling of the cost paid by month for all time or based on the provided start/end dates.

        _ = [print(i) for i in IncomingItem.objects.cost_by_month(
            start_date=timezone.datetime(2021, 5, 1), end_date=timezone.datetime(2021, 10, 1))]
        {'year': 2021, 'month': 9, 'month_extended_price': Decimal('3140.9300')}
        {'year': 2021, 'month': 8, 'month_extended_price': Decimal('2164.6400')}
        {'year': 2021, 'month': 7, 'month_extended_price': Decimal('3374.3900')}
        {'year': 2021, 'month': 6, 'month_extended_price': Decimal('4543.6600')}
        {'year': 2021, 'month': 5, 'month_extended_price': Decimal('4146.8900')}

        Args:
            start_date: Inclusive date from which to start.
            end_date: Inclusive date at which to end.

        Returns: A Queryset in order by year/month.
        """
        qs = self
        if start_date:
            qs = qs.filter(parent__action_date__gte=start_date)
        if end_date:
            qs = qs.filter(parent__action_date__lte=end_date)
        qs = qs.annotate(year=models.F('parent__action_date__year'), month=models.F('parent__action_date__month'))
        qs = qs.values('year', 'month').annotate(
            month_extended_price=models.Sum('extended_price'),
            groups=models.Count('parent__id', distinct=True)
        )
        qs = qs.order_by('-year', '-month')
        return qs

    def live_filter(self, terms=None, sources=None):
        pass


class IncomingItem(models.Model):
    # TODO: add position field so items stay in the order on the invoice.
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        IncomingItemGroup, on_delete=models.CASCADE, related_name="items", related_query_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="incoming_items")
    # Won't have this for OUT items for Sysco orders as the invoice just shows "OUT" for the quantity.
    ordered_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    # Does not include damaged/rejected items.
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)

    total_weight = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    pack_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    pack_tax = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    extended_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)

    line_item_position = models.PositiveSmallIntegerField("Position", null=True)

    comment = models.CharField(
        "Anything noteworthy about this item", max_length=1024, null=False, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

    objects = IncomingItemManager()

    class Meta:
        ordering = ("parent", "line_item_position", )

    def __str__(self):
        return self.item.item_name

    @staticmethod
    def autocomplete_search_fields():
        # TODO: Add item_code to autocomplete_search_fields
        return "id__icontains", "item__name__icontains"

    def get_common_item(self):
        return self.item.common_item

    def get_cost_per_unit(self):
        """
        Calculate the cost per thing that can be used.  For meats, this would be an individual roast.  For bags of
        flour, this is per one 50lb bag.  For individual serving milk/juice cartons, this is per carton.
        Returns: a decimal amount

        """
        # TODO: Should get_cost_per_unit use ordered or delivered quantity?
        # NOTE: Yes, I'm aware all the calculations are the same.  I keep thinking about how to handle partial packages
        # but that is not how the senior center currently works.  Think of this as a stub for if/when that changes.
        if self.total_weight:
            # if total_weight is populated, the pack_price is the per pound.
            # since there isn't anything currently storing the per-item actual weight, this is just an estimate.
            # We'd also need to know which of the items were used if we wanted that level of tracking.
            return self.extended_price / self.ordered_quantity / self.item.pack_quantity

        if self.item.individual_serving:
            # Ignore unit_size as it is likely for the individual serving containers.
            # "Treetop juice apple unswetnd 100% can" has pack_qty 48 and unit size "5.5oz".
            return self.extended_price / self.ordered_quantity / self.item.pack_quantity

        # By default, assume unit_size has nothing to do with the cost.
        return self.extended_price / self.ordered_quantity / self.item.pack_quantity

    def get_inventory_quantity(self):
        return self.item.get_delivered_unit_quantity(self.delivered_quantity)

    def recalculate_calculated_fields(self):
        if self.total_weight:
            # when given a total_weight, it is the weight of the entire order, not just a single pack.
            self.extended_price = self.pack_price * self.total_weight + self.pack_tax
        else:
            self.extended_price = self.pack_price * self.ordered_quantity + self.pack_tax

    def save(self, *args, **kwargs):
        # TODO: using ordered_quantity for now as get_cost_per_unit is doing so.
        self.recalculate_calculated_fields()
        super().save(*args, **kwargs)

    @property
    def unit_size(self):
        return self.item.unit_size
