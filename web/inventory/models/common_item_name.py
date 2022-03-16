from django.db import models

from scrap import models as sc_models, fields as sc_fields


class CommonItemNameGroup(sc_models.UUIDModel):
    # 'name' is the primary name of the group (nonstick spray).
    # Use 'names' to get all common names (cooking spray, pan spray, nonstick spray, pam).
    name = models.ForeignKey("inventory.CommonItemName", on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey("inventory.Category", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        pass


class CommonItemName(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False)
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.CASCADE, related_name="names", related_query_name="names",
        null=True
    )

    def __str__(self):
        return self.name
