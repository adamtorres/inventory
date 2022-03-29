from django import urls
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
    # TODO: need start/end dates where end defaults to start if not supplied.
    comment = sc_fields.CharField(help_text="Anything special about this usage as a whole")
    total_price = sc_fields.MoneyField()

    objects = UsageGroupManager()

    class Meta:
        ordering = ('-when', '-created', )

    def get_absolute_url(self):
        return urls.reverse("inventory:usagegroup_detail", kwargs={'pk': self.id})


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
    # TODO: used_quantity is of the unit size.  Second input to handle count?  On first use, would need to subtract a
    #  unit, then keep track of used count until it equals a unit.
    remaining_unit_quantity_snapshot = sc_fields.DecimalField()
    used_price = sc_fields.MoneyField()
    comment = sc_fields.CharField(help_text="Anything special about this specific item")

    objects = UsageManager()

    class Meta:
        ordering = (
            'item_in_stock__raw_incoming_item__rawitem_obj__category__name',
            'item_in_stock__raw_incoming_item__rawitem_obj__common_item_name_group__name__name',
            '-created',
        )

    @property
    def previous_unit_quantity(self):
        return self.remaining_unit_quantity_snapshot + self.used_quantity
