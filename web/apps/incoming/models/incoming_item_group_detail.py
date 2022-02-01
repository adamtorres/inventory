from django.db import models

import uuid

from .incoming_item_group import IncomingItemGroup


class IncomingItemGroupDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    incoming_group = models.ForeignKey(IncomingItemGroup, on_delete=models.CASCADE, related_name="details")
    name = models.CharField(max_length=1024, null=False, blank=False)
    content = models.CharField(max_length=1024, null=False, blank=True, default='')

    # Starts at 1 for each source
    position = models.PositiveSmallIntegerField("Position", null=True)

    class Meta:
        ordering = ['position']
