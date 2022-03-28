from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class UsageGroupManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('usages')
        return qs


class UsageGroup(sc_models.DatedModel):
    description = sc_fields.CharField(blank=False)
    when = models.DateField(help_text="when the described activity took place")
    comment = sc_fields.CharField(help_text="Anything special about this usage as a whole")

    objects = UsageGroupManager()


class UsageManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            "item_in_stock", "item_in_stock__raw_incoming_item",
            "item_in_stock__raw_incoming_item__rawitem_obj__source",
            "item_in_stock__raw_incoming_item__rawitem_obj__category",
            "item_in_stock__raw_incoming_item__rawitem_obj__common_item_name_group__name",)
        return qs


class Usage(sc_models.DatedModel):
    usage_group = models.ForeignKey(
        UsageGroup, on_delete=models.CASCADE, related_name='usages', related_query_name='usages')
    item_in_stock = models.ForeignKey("inventory.ItemInStock", on_delete=models.CASCADE)
    used_quantity = sc_fields.DecimalField()
    comment = sc_fields.CharField(help_text="Anything special about this specific item")

    objects = UsageManager()
