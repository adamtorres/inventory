from django.contrib.contenttypes import fields as ct_fields
from django.db import models
from django.utils import timezone


import uuid

from .source import Source
import scrap


class IncomingItemGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    # vendor order/donation instance
    #     a specific instance of incoming items group.  not a single item on the order.
    #     This might not be a complete order as some items might not have been delivered or were sent back as damaged.
    # TODO: any details about the order/donation
    descriptor = models.CharField("some uniquish descriptor", max_length=1024, null=False, blank=False)
    change = ct_fields.GenericRelation("inventory.Change", "source_object_id", "source_content_type")
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    # TODO: the default is UTC so evening dates are tomorrow.
    action_date = models.DateField(null=False, blank=False, default=timezone.now)

    def __str__(self):
        return f"{scrap.humanize_date(self.action_date)} - {scrap.snip_text(self.descriptor)}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "descriptor__icontains"

    def add_details(self):
        # Exclude details which already exist.  So the function can be repeated without duplication.
        q = self.source.detail_templates.exclude(name__in=self.details.values_list('name', flat=True))
        for detail in q.order_by('position'):
            self.details.create(name=detail.name, position=detail.position)
