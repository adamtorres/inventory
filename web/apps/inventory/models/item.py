from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid


class Item(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    common_item = models.ForeignKey("CommonItem", on_delete=models.CASCADE, related_name="items")
    original_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=4, null=False, blank=False)
    current_quantity = models.DecimalField(default=0, max_digits=10, decimal_places=4, null=False, blank=False)
    # TODO: cost and size info.  How is cost handled?  need to know the unit of measure.
    unit_size = models.CharField(max_length=1024, default='', null=False, blank=False)

    def __str__(self):
        # don't want to just str the common_item as that includes the other_names.
        return self.common_item.name

# inventory items
#     - these are the items actually in the building
#     - there wouldn't be just one of these for a given item.  There could be one for 50lb flour from sysco and another
#         for 5lb flour from broulims.
#     original quantity - how many when initially added
#     current quantity - how many right now
#     size - size of a single item as taken from the source item.  So we don't have to constantly link to the source.
#     cost and supporting fields ($/lb, $/count, or such)
