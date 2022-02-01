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
    unit_size = models.CharField(max_length=1024, null=False, blank=False, default='count')
    quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    # TODO: quantity, size, cost, etc.

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

    def __str__(self):
        return self.item.name

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "item__name__icontains"
