from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class Order(sc_models.UUIDModel):
    item_pack = models.ForeignKey("market.ItemPack", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    date_made = models.DateField()
    pickup_date = models.DateField()
    who = sc_fields.CharField()
    sale_price_per_pack = sc_fields.MoneyField()
    sale_price = sc_fields.MoneyField()
    material_cost_per_pack = sc_fields.MoneyField(help_text="cost of materials for a single pack.")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for the order.")
