from django.contrib.contenttypes import fields as ct_fields
from django.db import models
from django.utils import timezone

import uuid

import scrap


class Adjustment(scrap.ChangeSourceMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: what kind of adj (audit, damaged, other group-level thing), when
    type = models.CharField("Adjustment type", max_length=1024, null=False, blank=False)
    who = models.CharField("Who made the adjustment", max_length=1024, null=False, blank=False)
    change = ct_fields.GenericRelation(
        "inventory.Change", "source_object_id", "source_content_type", related_query_name="adjustment")
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    action_date = models.DateField(null=False, blank=False, default=timezone.now)

    def __str__(self):
        converted = "✓" if self.is_converted else ""
        return f"{converted}{scrap.humanize_date(self.action_date)} - {scrap.snip_text(self.type)} - {scrap.snip_text(self.who)}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "type__icontains"
