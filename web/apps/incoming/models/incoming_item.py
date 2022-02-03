from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid

from .incoming_item_group import IncomingItemGroup
from .item import Item


class IncomingItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(IncomingItemGroup, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="incoming_items")
    # Won't have this for OUT items for Sysco orders as the invoice just shows "OUT" for the quantity.
    ordered_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    # Does not include damaged/rejected items.
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)

    total_weight = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    unit_tax = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    extended_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)

    comment = models.CharField(
        "Anything noteworthy about this item", max_length=1024, null=False, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

    def __str__(self):
        return self.item.item_name

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "item__name__icontains"

    def get_common_item(self):
        return self.item.common_item

    def get_inventory_quantity(self):
        return self.delivered_quantity * self.item.pack_quantity
