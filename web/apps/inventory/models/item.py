from django.contrib.postgres import aggregates as pg_agg
from django.db import models

import uuid


class ItemManager(models.Manager):
    def get_consolidated_inventory(self):
        """
        Groups the common items and totals the quantities.
        """
        # exclude anything that has 0 or less quantity.  Should include negative here or in a report?
        qs = self.exclude(current_quantity__lte=0).select_related('common_item')
        return qs.values('common_item', common_item_name=models.F('common_item__name')).annotate(
            other_names=pg_agg.StringAgg('common_item__other_names__name', ', ', default=models.Value(''), ordering=()),
            quantity=models.Sum('current_quantity')
        ).order_by('common_item_name')
    # TODO: need to add a category group/sort when category is added to the model.
    # def get_queryset(self):
    #     return super().get_queryset().filter(author='Roald Dahl')


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    common_item = models.ForeignKey("CommonItem", on_delete=models.CASCADE, related_name="items")
    original_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=4, null=False, blank=False)
    current_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=4, null=False, blank=False)
    # TODO: cost and size info.  How is cost handled?  need to know the unit of measure.
    unit_size = models.CharField(max_length=1024, default='', null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

    objects = ItemManager()

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
