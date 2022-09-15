from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class OnSaleItemPack(sc_models.UUIDModel):
    item_pack = models.ForeignKey("market.ItemPack", on_delete=models.CASCADE)
    date_made = models.DateField()
    packs_made = models.IntegerField(default=0, help_text="how many packs put up for sale")
    date_frozen = models.DateField(null=True, blank=True)
    packs_frozen = models.IntegerField(
        null=True, blank=True, default=0, help_text="how many packs were put into freezer")
    sale_price_fresh = sc_fields.MoneyField()
    sale_price_frozen = sc_fields.MoneyField(help_text="Usually a dollar off from fresh price")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for the pack.")
