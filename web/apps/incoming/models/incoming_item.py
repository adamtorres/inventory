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
    # TODO: quantity, size, cost, etc.

    def __str__(self):
        return self.item.name
