from django.db import models

from scrap import models as sc_models, fields as sc_fields


class RawItem(sc_models.DatedModel):
    source = models.ForeignKey(
        "inventory.Source", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items")
    # TODO: first/last order dates, avg price, last price

    name = sc_fields.CharField(blank=False)
    unit_size = sc_fields.CharField()
    pack_quantity = sc_fields.DecimalField()

    category = models.ForeignKey(
        "inventory.Category", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items")
    better_name = sc_fields.CharField(help_text="Less cryptic item name")
    item_code = sc_fields.CharField()
    extra_code = sc_fields.CharField()
    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")

    # Primary common item name group
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'source', 'name', 'unit_size', 'pack_quantity', name='source-name-unit_size-pack_quantity'),
        ]

    def __str__(self):
        tmp = f"{self.source}, {self.name}"
        if self.pack_quantity != 1:
            tmp += f", {self.pack_quantity}"
        if self.unit_size:
            tmp += f", {self.unit_size}"
        return tmp

    def get_filter(self):
        """
        Returns a filter that can be used to find this item in RawIncomingItem before the foreign key is set.
        """
        return models.Q(
            source_obj=self.source, name=self.name, unit_size=self.unit_size, pack_quantity=self.pack_quantity)
