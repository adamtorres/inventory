from django.db import models

from scrap import models as sc_models


class ItemPack(sc_models.UUIDModel):
    item = models.ForeignKey(
        "market.Item", on_delete=models.CASCADE, related_name="item_packs", related_query_name="item_packs")
    quantity = models.IntegerField(default=1, help_text="1pk, 3pk, 6pk, 8pk, dz")

    class Meta:
        ordering = ['item', 'quantity']

    def __str__(self):
        return f"{self.quantity_str()} {self.item}"

    def quantity_str(self):
        return "dz" if self.quantity == 12 else f"{self.quantity}pk"
