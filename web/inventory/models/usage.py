from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class UsageGroup(sc_models.DatedModel):
    description = sc_fields.CharField()
    when = models.DateField(help_text="when the described activity took place")


class Usage(sc_models.DatedModel):
    usage_group = models.ForeignKey(UsageGroup, on_delete=models.CASCADE)
    item_in_stock = models.ForeignKey("inventory.ItemInStock", on_delete=models.CASCADE)
    used_quantity = sc_fields.DecimalField()
