from collections import defaultdict

from django.contrib.postgres import aggregates as pg_agg
from django.db import models

import uuid

from scrap import models as sc_models


class ItemManager(models.Manager, sc_models.FilterMixin):
    autocomplete_fields = [
        "common_item__name", "common_item__other_names__name", "common_item__incoming_items__name",
        "common_item__incoming_items__better_name"]
    filter_prefetch = ['common_item', 'location']
    filter_order = ['common_item__name', 'created']
    autocomplete_initial_qs = 'available_items'

    def available_items(self):
        qs = self.exclude(current_quantity__lte=0)
        return qs

    def get_consolidated_inventory(self):
        """
        Groups the common items and totals the quantities.
        """
        # exclude anything that has 0 or less quantity.  Should include negative here or in a report?
        qs = self.exclude(current_quantity__lte=0).select_related('common_item', 'common_item__category', 'location')
        qs = qs.values(
            'common_item',
            common_item_name=models.F('common_item__name'),
            category=models.F('common_item__category__name'),
        )
        qs = qs.annotate(
            total_quantity=models.Sum('current_quantity'),
            total_cost=models.Sum(models.F('unit_cost') * models.F('current_quantity')),
            # TODO: This was making the totals incorrect.  Low priority but would like to add other names back.
            # other_names=pg_agg.StringAgg(
            #     'common_item__other_names__name', ', ', default=models.Value(''),
            #     ordering='common_item__other_names__name', distinct=True),
            # Odd that the StringAgg for other names breaks totals but locations doesn't.  Must be in how an item has
            # exactly one location but could have many other names.  The multiple locations comes from multiple items.
            locations=pg_agg.StringAgg(
                'location__name', ', ', default=models.Value(''), ordering='location__name', distinct=True),
        )
        return qs
        # Returns queryset of:
        # {
        #     'common_item': UUID('4c6a3ce1-8a24-48c7-9d1c-249394a3a381'),
        #     'common_item_name': 'ground beef',
        #     'category': 'meats',
        #     'total_quantity': Decimal('3.0000'),
        #     'total_cost': Decimal('90.06000000'),
        #     'locations': 'Freezer, Refrigerator'}

    def get_categorized_inventory(self, categories=None):
        """
        If categories is None(default), then will not limit returned categories.  If a string, will return the one
        category (though, could use Category.common_items.items.all()).  If a list or tuple, will return the dict for
        the specified categories.
        Returns:
            a dict with categories as keys and iterable of items as values.
        """
        qs = self.get_consolidated_inventory()
        if isinstance(categories, str):
            qs = qs.filter(category__in=[categories])
        elif isinstance(categories, (list, tuple)):
            qs = qs.filter(category__in=categories)
        items = defaultdict(list)
        for item in qs:
            items[item["category"]].append(item)
        return items

    def autocomplete_search(self, terms):
        """
        Provided a single or list of terms, search item names, common names, and other names for the terms.  Return a
        queryset of the found items.  Only items with positive current_quantity are returned.

        Args:
            terms: single string or list of strings.

        Returns:
            queryset with the result.
        """
        qs = super().autocomplete_search(terms)
        qs = qs.distinct('common_item__name', 'created', 'id')
        return qs


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    common_item = models.ForeignKey("CommonItem", on_delete=models.CASCADE, related_name="items")
    original_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=4, null=False, blank=False)
    current_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=4, null=False, blank=False)
    # TODO: cost and size info.  How is cost handled?  need to know the unit of measure.
    unit_size = models.CharField(max_length=1024, default='', null=False, blank=False)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    location = models.ForeignKey(
        "inventory.Location", on_delete=models.CASCADE, null=True, blank=False, related_name='items')

    objects = ItemManager()

    class Meta:
        ordering = ('common_item__name', 'created', )

    def __str__(self):
        # don't want to just str the common_item as that includes the other_names.
        return self.common_item.name

    @property
    def extended_cost(self):
        return self.unit_cost * self.current_quantity
# inventory items
#     - these are the items actually in the building
#     - there wouldn't be just one of these for a given item.  There could be one for 50lb flour from sysco and another
#         for 5lb flour from broulims.
#     original quantity - how many when initially added
#     current quantity - how many right now
#     size - size of a single item as taken from the source item.  So we don't have to constantly link to the source.
#     cost and supporting fields ($/lb, $/count, or such)
