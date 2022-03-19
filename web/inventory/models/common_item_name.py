from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class CommonItemNameGroupManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('name')
        return qs


class CommonItemNameGroup(sc_models.UUIDModel):
    # 'name' is the primary name of the group (nonstick spray).
    # Use 'names' to get all common names (cooking spray, pan spray, nonstick spray, pam).
    name = models.ForeignKey(
        "inventory.CommonItemName", on_delete=models.SET_NULL, null=True, related_name="primary_groups")
    category = models.ForeignKey("inventory.Category", on_delete=models.SET_NULL, null=True)

    uncommon_item_names = pg_fields.ArrayField(
        models.CharField(max_length=1024, null=False, blank=False), null=False, blank=True, default=list)

    objects = CommonItemNameGroupManager()

    def __str__(self):
        if self.name:
            return self.name.name
        return f"Unnamed CommonItemNameGroup({self.id})"


class CommonItemName(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False)
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.CASCADE, related_name="names", related_query_name="names",
        null=True
    )

    def __str__(self):
        return self.name
