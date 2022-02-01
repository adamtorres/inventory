from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid


class Change(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link this to a vendor order, donation, local store pickup, etc.  Actual instance of change, not the company.
    # This is the order or donation group object.  Not a specific item within.
    # This could also link to usage forms or inventory adjustments
    source = models.ForeignKey("incoming.IncomingItemGroup", on_delete=models.CASCADE, null=True, blank=True)
    # TODO: rework so this can link to incoming.IncomingItemGroup, Usage, or Adjustment?

# inventory change
#     - groups changes to items
#     - this isn't just incoming.  This includes usage forms.
#     link to specific order or donation in case we need to see an original

    def __str__(self):
        return f"Group of inventory changes {self.id}"
