from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid

from .item import Item
from .usage import Usage


class UsageItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(Usage, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="usage_items")
    # TODO: quantity, size, cost, etc.
    unit_size = models.CharField(max_length=1024, null=False, blank=False, default='count')
    quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

    def __str__(self):
        # TODO: should item changes store the name at the time of creation in case it changes?
        # Also, doing it as item.common_item.name depends on children knowing more than one level up.
        return self.item.common_item.name

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "item__common_item__name__icontains", "item__common_item__other_names__name__icontains"

    def get_common_item(self):
        return self.item.common_item
