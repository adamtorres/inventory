from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class ItemManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('source')
        return qs

    def with_in_stock_quantities(self, qs=None):
        qs = (qs or self).values('source__name', 'name', 'raw_items__unit_size').annotate(
            total_pack_quantity=models.Sum('raw_items__raw_incoming_items__in_stock__remaining_pack_quantity')
        ).order_by('source__name', 'name', 'raw_items__unit_size')
        current_source = None
        current_name = None
        current_unit_size = None
        current_quantity = 0
        current_quantities = []
        items_with_quantities = []
        for item_with_unit in qs:
            if current_source != item_with_unit['source__name'] or current_name != item_with_unit['name']:
                # complete change of item.
                if current_source:
                    current_quantities.append({"unit_size": current_unit_size, "pack_quantity": current_quantity})
                    items_with_quantities.append(
                        {"source": current_source, "name": current_name, "quantities": current_quantities})
                current_source = item_with_unit['source__name']
                current_name = item_with_unit['name']
                current_unit_size = item_with_unit['raw_items__unit_size']
                current_quantities = []
                current_quantity = 0
            if current_unit_size != item_with_unit['raw_items__unit_size']:
                current_quantities.append({"unit_size": current_unit_size, "pack_quantity": current_quantity})
                current_unit_size = item_with_unit['raw_items__unit_size']
                current_quantity = 0
            current_quantity += item_with_unit['total_pack_quantity']
        if current_quantity:
            current_quantities.append({"unit_size": current_unit_size, "pack_quantity": current_quantity})
        if current_quantities:
            items_with_quantities.append(
                {"source": current_source, "name": current_name, "quantities": current_quantities})
        return items_with_quantities


class Item(sc_models.UUIDModel):
    source = models.ForeignKey("inventory.Source", on_delete=models.CASCADE)
    name = sc_fields.CharField(blank=False)

    objects = ItemManager()

    class Meta:
        ordering = ('source__name', 'name')
        constraints = [
            models.UniqueConstraint('source', 'name', name='item-source-name'),
        ]

    def __str__(self):
        return f"{self.source} / {self.name}"

    def get_item_filter(self):
        """
        Returns a filter that can be used to find this item in RawItem before the foreign key is set.
        """
        return models.Q(source=self.source, name=self.name)
