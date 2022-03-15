from django.db import models

from scrap import models as sc_models, fields as sc_fields


class CommonItemName(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False)
    raw_items = models.ManyToManyField(
        "inventory.RawItem", related_name="common_item_names", related_query_name="common_item_names")
