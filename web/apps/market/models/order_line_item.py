import math

from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class OrderLineItem(sc_models.UUIDModel):
    order = models.ForeignKey(
        "market.Order", on_delete=models.CASCADE, related_name="line_items", related_query_name="line_items")
    line_item_position = models.IntegerField(default=0)

    item = models.ForeignKey("market.Item", on_delete=models.SET_NULL, null=True)
    item_str = sc_fields.CharField(
        blank=True, null=True, help_text="Backup of str(item) in case the item is deleted.")
    quantity = models.IntegerField()
    sale_price_per_pack = sc_fields.MoneyField()
    sale_price = sc_fields.MoneyField()
    material_cost_per_pack = sc_fields.MoneyField(help_text="cost of materials for a single pack.")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for the order.")

    class Meta:
        ordering = ['order', 'line_item_position']

    def __str__(self):
        # TODO: save a local copy of item str so it doesn't hit the db again and in case item changes.
        return f"{sc_utils.reduce_dozens(self.quantity)} {self.item or self.item_str}"

    def calculate_totals(self, commit=True):
        if self.item:
            material_cost_per_pack = self.item.material_cost_per_item
        else:
            # The Item was removed after this order was created.  Do not change the cost.
            material_cost_per_pack = self.material_cost_per_pack
        material_cost = float(material_cost_per_pack) * self.quantity
        sale_price = float(self.sale_price_per_pack) * (self.quantity / 12)
        needs_saved = False
        if self.material_cost_per_pack != material_cost_per_pack:
            self.material_cost_per_pack = material_cost_per_pack
            needs_saved = True
        if self.material_cost != material_cost:
            self.material_cost = material_cost
            needs_saved = True
        if self.sale_price != sale_price:
            self.sale_price = sale_price
            needs_saved = True
        if commit and needs_saved:
            self.save()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):

        if self.item:
            item_str = str(self.item)
            if self.item_str != item_str:
                self.item_str = item_str
                if update_fields is not None:
                    update_fields.add('item_str')
        return super().save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
