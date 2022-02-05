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
    pack_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    pack_tax = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    extended_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)

    comment = models.CharField(
        "Anything noteworthy about this item", max_length=1024, null=False, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

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

    @property
    def unit_size(self):
        return self.item.unit_size
