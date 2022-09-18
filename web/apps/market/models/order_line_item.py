from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class OrderLineItem(sc_models.UUIDModel):
    order = models.ForeignKey(
        "market.Order", on_delete=models.CASCADE, related_name="line_items", related_query_name="line_items")
    line_item_position = models.IntegerField(default=0)

    item_pack = models.ForeignKey("market.ItemPack", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    sale_price_per_pack = sc_fields.MoneyField()
    sale_price = sc_fields.MoneyField()
    material_cost_per_pack = sc_fields.MoneyField(help_text="cost of materials for a single pack.")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for the order.")

    def __str__(self):
        # TODO: save a local copy of item_pack str so it doesn't hit the db again and in case item_pack changes.
        return f"{self.quantity}x {self.item_pack}"

