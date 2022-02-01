from django.db import models

import uuid

from .source import Source


class IncomingItemGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    # vendor order/donation instance
    #     a specific instance of incoming items group.  not a single item on the order.
    #     This might not be a complete order as some items might not have been delivered or were sent back as damaged.
    # TODO: any details about the order/donation
    descriptor = models.CharField("some uniquish descriptor", max_length=1024, null=False, blank=False)

    def __str__(self):
        return f"a set of incoming items {self.id}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "descriptor__icontains"
