from django.contrib.contenttypes import fields as ct_fields
from django.db import models
from django.utils import timezone


import uuid

from .source import Source
import scrap


class IncomingItemGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE)
    descriptor = models.CharField("some uniquish descriptor", max_length=1024, null=False, blank=True, default='')
    change = ct_fields.GenericRelation("inventory.Change", "source_object_id", "source_content_type")

    comment = models.CharField(
        "Anything noteworthy about this order", max_length=1024, null=False, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    # TODO: guessing the default is UTC timezone so filling out a form in the evening creates dates in tomorrow.
    action_date = models.DateField(null=False, blank=False, default=timezone.now)

    _total_price = None
    _total_packs = None

    def __str__(self):
        return f"{scrap.humanize_date(self.action_date)} - {scrap.snip_text(self.descriptor)} - ${self.total_price}"

    def _populate_calculated_fields(self):
        values = self.items.aggregate(
            total_price=models.Sum('extended_price'), total_packs=models.Sum('delivered_quantity'))
        self._total_price = values["total_price"]
        self._total_packs = values["total_packs"]

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "descriptor__icontains"

    def add_details(self):
        # Exclude details which already exist.  So the function can be repeated without duplication.
        q = self.source.detail_templates.exclude(name__in=self.details.values_list('name', flat=True))
        for detail in q.order_by('position'):
            self.details.create(name=detail.name, position=detail.position)

    def invalidate_calculated_fields(self):
        self._total_price = None
        self._total_packs = None

    @property
    def total_packs(self):
        if self._total_packs is None:
            self._populate_calculated_fields()
        return self._total_packs

    @property
    def total_price(self):
        if self._total_price is None:
            self._populate_calculated_fields()
        return self._total_price
