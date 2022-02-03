from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid

import scrap


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey("incoming.Source", on_delete=models.CASCADE, related_name="items")
    name = models.CharField("Probably cryptic item name", max_length=1024, null=False, blank=False)
    common_item = models.ForeignKey("inventory.CommonItem", on_delete=models.CASCADE, related_name="incoming_items")
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    do_not_inventory = models.BooleanField(default=False, null=False, blank=False)

    # A single package can have multiple items.
    pack_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    unit_size = models.CharField(max_length=1024, null=False, blank=False, default='count')

    # TODO: How to convert this item's quantity to a usable inventory quantity?  Should it just be up to the user?

# vendor/donation items
#     - This is not items on an order.  This is just a way to convert between vendor and inventory.
#     - There might be multiple items that are actually the same thing as vendors sometimes change item
#           numbers/descriptions.
#     - names are specific to vendor/donator
#     some kind of link to an inventory item so we can easily convert an incoming item to an inventory item.
#     how to convert between this item's quantity to inventory item's quantity.

# incoming items
#     a complete list of items that come from outside.
#     This is not actual incoming items.  This is a list of names which also link to common items.

    def __str__(self):
        return f"{self.source.name} / {self.item_name}"

    @property
    def item_name(self):
        return f"{scrap.undecimal(self.pack_quantity)} {self.unit_size}, {self.name}"
