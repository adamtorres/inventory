from django.contrib.contenttypes import fields as ct_fields
from django.db import models
from django import urls
from django.utils import timezone


import uuid

from .source import Source
import scrap


class IncomingItemGroupManager(models.Manager):
    def list_groups(self, start_date=None):
        qs = IncomingItemGroup.objects.all().select_related('source')
        if start_date:
            qs = qs.filter(action_date__gte=start_date)
        qs = qs.annotate(
            converted_state=models.Case(
                models.When(converted_datetime__isnull=False, then=models.Value('converted')),
                default=models.Value('not converted')),
            source_name=models.F('source__name'),
            total_cost=models.Sum('items__extended_price'),
            total_items=models.Count('items'),
            total_pack_quantity=models.Sum('items__delivered_quantity'),
        )
        qs = qs.order_by('-converted_state', '-action_date')
        return qs

    def list_groups_by_converted_state(self, start_date=None):
        qs = self.list_groups(start_date=start_date)
        conv = list(qs.filter(converted_state='converted'))
        not_conv = list(qs.filter(converted_state='not converted'))
        return {'converted': conv, 'not_converted': not_conv}


class IncomingItemGroup(scrap.ChangeSourceMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='item_groups')
    descriptor = models.CharField("some uniquish descriptor", max_length=1024, null=False, blank=True, default='')
    change = ct_fields.GenericRelation(
        "inventory.Change", "source_object_id", "source_content_type", related_query_name="incomingitemgroup")

    comment = models.CharField(
        "Anything noteworthy about this order", max_length=1024, null=False, blank=True, default='')

    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    # TODO: guessing the default is UTC timezone so filling out a form in the evening creates dates in tomorrow.
    action_date = models.DateField(null=False, blank=False, default=timezone.now)

    _total_price = None
    _total_packs = None

    objects = IncomingItemGroupManager()

    def __str__(self):
        converted = "✓" if self.is_converted else ""
        return f"{converted}{scrap.humanize_date(self.action_date)} - {scrap.snip_text(self.descriptor)}" \
               f" - $ {self.total_price}"

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

    # def get_absolute_url(self):
    #     return urls.reverse('incominggroup-detail', kwargs={'pk': self.pk})

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
