from django.db import models
from django.utils import timezone

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class Order(sc_models.UUIDModel):
    item_pack = models.ForeignKey("market.ItemPack", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date_ordered = models.DateField(default=timezone.now)
    date_made = models.DateField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    who = sc_fields.CharField()
    sale_price_per_pack = sc_fields.MoneyField()
    sale_price = sc_fields.MoneyField()
    material_cost_per_pack = sc_fields.MoneyField(help_text="cost of materials for a single pack.")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for the order.")

    def __str__(self):
        # TODO: save a local copy of item_pack str so it doesn't hit the db again and in case item_pack changes.
        return f"{self.quantity}x {self.item_pack}"

    def state(self):
        if not self.date_made:
            return "Ordered"
        if not self.pickup_date:
            return "Made"
        return "Completed"
