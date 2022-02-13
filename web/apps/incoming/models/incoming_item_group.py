from django.apps import apps
from django.contrib.contenttypes import fields as ct_fields
from django.db import models
from django import urls
from django.utils import timezone


import uuid

from .source import Source
import scrap


class IncomingItemGroupManager(models.Manager):
    def list_groups(self, start_date=None, values=False):
        # TODO: does this need reworked after adding total_price and total_packs?
        qs = IncomingItemGroup.objects.all().select_related('source')
        if start_date:
            qs = qs.filter(action_date__gte=start_date)
        qs = qs.annotate(
            converted_state=models.Case(
                models.When(converted_datetime__isnull=False, then=models.Value('')),
                default=models.Value('nope')),
            source_name=models.F('source__name'),
            total_items=models.Count('items'),
        )
        qs = qs.order_by('-converted_state', '-action_date')
        if values:
            return qs.values()
        return qs

    def list_groups_by_converted_state(self, start_date=None, values=False):
        qs = self.list_groups(start_date=start_date)
        if values:
            conv = list(qs.filter(converted_state='converted').values())
            not_conv = list(qs.filter(converted_state='not converted').values())
        else:
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

    total_price = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    total_packs = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)

    objects = IncomingItemGroupManager()

    def __str__(self):
        converted = "✓" if self.is_converted else ""
        return f"{converted}{scrap.humanize_date(self.action_date)} - {scrap.snip_text(self.descriptor)}" \
               f" - $ {self.total_price}"

    def recalculate_calculated_fields(self):
        values = self.items.aggregate(
            total_price=models.Sum('extended_price'), total_packs=models.Sum('delivered_quantity'))
        changed = False
        if self.total_price != values["total_price"]:
            self.total_price = values["total_price"]
            changed = True
        if self.total_packs != values["total_packs"]:
            self.total_packs = values["total_packs"]
            changed = True
        if changed:
            self.save()

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "descriptor__icontains"

    def add_details(self):
        # Exclude details which already exist.  So the function can be repeated without duplication.
        q = self.source.detail_templates.exclude(name__in=self.details.values_list('name', flat=True))
        for detail in q.order_by('position'):
            self.details.create(name=detail.name, position=detail.position)

    def get_absolute_url(self):
        return urls.reverse('incoming_group', kwargs={'pk': self.pk})

    def invalidate_calculated_fields(self):
        self._total_price = None
        self._total_packs = None
