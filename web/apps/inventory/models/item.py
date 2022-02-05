from django.contrib.postgres import aggregates as pg_agg
from django.db import models

import uuid


class ItemManager(models.Manager):
    def get_consolidated_inventory(self):
        """
        Groups the common items and totals the quantities.
        """
        # exclude anything that has 0 or less quantity.  Should include negative here or in a report?
        qs = self.exclude(current_quantity__lte=0).select_related('common_item', 'common_item__category')
        qs = qs.values(
            'common_item', 'current_quantity',
            common_item_name=models.F('common_item__name'),
            category=models.F('common_item__category__name'),
            current_quantity_cost=models.F('unit_cost') * models.F('current_quantity'),
        )
        qs = qs.values(
            'common_item', 'category', 'common_item_name'
        )
        qs = qs.annotate(
            total_quantity=models.Sum('current_quantity'),
            total_cost=models.Sum('current_quantity_cost'),
        )
        # other_names = pg_agg.StringAgg(
        #     'common_item__other_names__name', ', ', default=models.Value(''), ordering=()),
        # locations = pg_agg.StringAgg(
        #     'location__name', ', ', default=models.Value(''), ordering='location__name', distinct=True),
        return qs
        # Returns queryset of:
        #     {'common_item': UUID('135f455f-39d3-4975-98b6-3a0c223cfd64'),
        #      'common_item_name': 'beef roast bottom round flat', 'category': 'meats', 'other_names': '',
        #      'locations': '', 'quantity': Decimal('7.0000')}

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
        pass

    # def get_queryset(self):
    #     return super().get_queryset().filter(author='Roald Dahl')


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
        pass

    def __str__(self):
        # don't want to just str the common_item as that includes the other_names.
        return self.common_item.name

# inventory items
#     - these are the items actually in the building
#     - there wouldn't be just one of these for a given item.  There could be one for 50lb flour from sysco and another
#         for 5lb flour from broulims.
#     original quantity - how many when initially added
#     current quantity - how many right now
#     size - size of a single item as taken from the source item.  So we don't have to constantly link to the source.
#     cost and supporting fields ($/lb, $/count, or such)
