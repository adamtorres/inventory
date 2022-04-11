from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class MissingItemInStock(sc_models.DatedModel):
    # Need to be able to assign a RawItem or CommonItemNameGroup if one exists.
    # Need to be able to dynamically create at least a CommonItemNameGroup if one doesn't exist.

    raw_item = models.ForeignKey("inventory.RawItem", on_delete=models.CASCADE, null=True, blank=True)
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.CASCADE, null=True, blank=True)

    reason_for_missing = sc_fields.CharField(help_text="Any idea why this item isn't in the inventory")

    class Meta:
        constraints = [
            # TODO: MissingItemInStock(RawItem, CING) Should both being null be allowed?
            models.CheckConstraint(
                check=(
                    models.Q(raw_item__isnull=True, common_item_name_group__isnull=True) |
                    models.Q(raw_item__isnull=False, common_item_name_group__isnull=True) |
                    models.Q(raw_item__isnull=True, common_item_name_group__isnull=False)),
                name='missing_item_with_rawitem_xor_cing'),
        ]
