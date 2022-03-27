from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class ItemInStockManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'raw_incoming_item', 'raw_incoming_item__rawitem_obj', 'raw_incoming_item__rawitem_obj__source',
            'raw_incoming_item__rawitem_obj__category',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name'
        )
        return qs

    def in_stock(self):
        return self.exclude(remaining_unit_quantity__lte=0)


class ItemInStock(sc_models.DatedModel):
    raw_incoming_item = models.OneToOneField(
        "inventory.RawIncomingItem", on_delete=models.CASCADE, related_name="in_stock", related_query_name="in_stock")
    original_unit_quantity = sc_fields.DecimalField(help_text="delivered_quantity * pack_quantity")
    remaining_unit_quantity = sc_fields.DecimalField()
    # remaining_unit_quantity = models.IntegerField(
    # default=1, help_text="For unit_size=ct/dz, this converts that to a number")

    objects = ItemInStockManager()

    class Meta:
        ordering = (
            'raw_incoming_item__rawitem_obj__source__name',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name__name', 'raw_incoming_item__delivery_date',
            'raw_incoming_item__created',
        )
