from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid


class CommonItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("primary name", max_length=1024, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    location = models.ForeignKey(
        "inventory.Location", on_delete=models.CASCADE, null=True, blank=True, related_name='common_items')
    category = models.ForeignKey(
        "inventory.Category", on_delete=models.CASCADE, null=True, blank=True, related_name='common_items')

    # TODO: link to vendor common items
    # TODO: unit of measure
    # TODO: closed quantity flag

    def __str__(self):
        other_names = "', '".join(self.other_names.all().values_list('name', flat=True))
        if other_names:
            return f"{self.name} a.k.a. '{other_names}'"
        return self.name

    def make_item(self, unit_size):
        # Create a 0 quantity item from this common item.
        return self.items.create(unit_size=unit_size, location=self.location)

# ? items
#     - provides a listing of all items which can be used as a dictionary/lookup table
#     names are basic - not vendor specific
#     link to vendor/donation items to provide a way to automatically link incoming items to inventory items.
#     unit of measure
#         uom could be a specific size bag if the count is of unopened containers.
#         uom could be a volume, weight, or count.  ex: liquid, powder, or egg.
#     closed quantity - flag to tell if this item should count only unopened containers or any partial quantities.
#         this should be set as a default to whatever is most common.  maybe a setting or a db value?


class CommonItemOtherName(models.Model):
    """
    Alternate names for a common item.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("alternate name", max_length=1024, null=False, blank=False)
    common_item = models.ForeignKey(CommonItem, on_delete=models.CASCADE, related_name="other_names")

    def __str__(self):
        return f"({self.common_item.name}) {self.name}"
