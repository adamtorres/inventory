from django.contrib.contenttypes import fields as ct_fields
from django.db import models
from django.utils import timezone

import uuid

import scrap


class Usage(scrap.ChangeSourceMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: who used, when
    who = models.CharField("Who used this stuff", max_length=1024, null=False, blank=False)
    change = ct_fields.GenericRelation("inventory.Change", "source_object_id", "source_content_type")
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    action_date = models.DateField(null=False, blank=False, default=timezone.now)

    # When converting to a Change, the quantity here needs to be negated.
    flip_quantity = True

    def __str__(self):
        converted = "✓" if self.is_converted else ""
        return f"{converted}{scrap.humanize_date(self.action_date)} - {scrap.snip_text(self.who)}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "who__icontains"
