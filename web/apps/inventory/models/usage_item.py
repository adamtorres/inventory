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

    def __str__(self):
        # TODO: should item changes store the name at the time of creation in case it changes?
        # Also, doing it as item.common_item.name depends on children knowing more than one level up.
        return self.item.common_item.name
