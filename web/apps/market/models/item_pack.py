from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields
from market import utils


class ItemPack(sc_models.UUIDModel):
    item = models.ForeignKey(
        "market.Item", on_delete=models.CASCADE, related_name="item_packs", related_query_name="item_packs")
    quantity = models.IntegerField(default=1, help_text="1pk, 3pk, 6pk, 8pk, dz")
    material_cost_per_pack = sc_fields.MoneyField(null=True, blank=True)
    suggested_sale_price_per_pack = sc_fields.MoneyField(null=True, blank=True)

    class Meta:
        ordering = ['item', 'quantity']

    def __str__(self):
        return f"{self.quantity_str()} {self.item}"

    def calculate_material_cost(self, commit=True):
        material_cost_per_pack = self.item.material_cost_per_item * self.quantity
        if self.material_cost_per_pack != material_cost_per_pack:
            self.material_cost_per_pack = material_cost_per_pack
            if commit:
                self.save()

    def calculate_suggested_sale_price(self, commit=True):
        suggested_sale_price_per_pack = utils.get_suggested_price(self.item.category, self.quantity) or 0
        if suggested_sale_price_per_pack:
            if self.suggested_sale_price_per_pack != suggested_sale_price_per_pack:
                self.suggested_sale_price_per_pack = suggested_sale_price_per_pack
                if commit:
                    self.save()

    def quantity_str(self):
        return "dz" if self.quantity == 12 else f"{self.quantity}pk"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.calculate_material_cost(commit=False)
        self.calculate_suggested_sale_price(commit=False)
        return super().save(
            force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
