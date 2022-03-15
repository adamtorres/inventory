from django.db import models

from scrap import models as sc_models, fields as sc_fields


class RawItem(sc_models.DatedModel):
    source = models.ForeignKey(
        "inventory.Source", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items")
    # TODO: first/last order dates, avg price, last price
    category = sc_fields.CharField(blank=False, help_text="meat, dairy, produce, etc.")
    name = sc_fields.CharField(blank=False)
    better_name = sc_fields.CharField(help_text="Less cryptic item name")
    item_code = sc_fields.CharField()
    extra_code = sc_fields.CharField()
    unit_size = sc_fields.CharField()
    pack_quantity = sc_fields.DecimalField()
    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")

    # Primary common item name
    common_item_name = models.ForeignKey("inventory.CommonItemName", on_delete=models.SET_NULL, null=True, blank=True)
