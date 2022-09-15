from django.db import models

from scrap import models as sc_models


class ItemPack(sc_models.UUIDModel):
    item = models.ForeignKey("market.Item", on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, help_text="1pk, 3pk, 6pk, 8pk, dz")
