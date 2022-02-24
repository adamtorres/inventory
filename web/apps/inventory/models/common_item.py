from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.contrib.postgres import aggregates as pg_agg
from django.db import models

import uuid


class CommonItemManager(models.Manager):
    def autocomplete_search(self, terms):
        """
        Provided a single or list of terms, search item names and other names for the terms.  Return a queryset of the
        found items along with current quantity in stock.

        Args:
            terms: single string or list of strings.

        Returns:
            queryset with the result.
        """
        if not terms:
            return self.none()
        if isinstance(terms, str):
            terms = [terms]
        # TODO: some of this autocomplete stuff is duplicated.  Base class?  Or at least a scrap function?

        term_q = models.Q()

        for term in terms:
            term_q = (
                term_q | models.Q(name__icontains=term) |
                models.Q(other_names__name__icontains=term) |
                models.Q(incoming_items__name__icontains=term) |
                models.Q(incoming_items__better_name__icontains=term)
            )
        qs = self.prefetch_related('other_names', 'location', 'category').filter(term_q)
        qs = qs.annotate(
            quantity=models.Sum('items__current_quantity'),
            extended_price=models.Sum(models.F('items__unit_cost')*models.F('items__current_quantity')),
            groups=models.Count(
                models.Case(
                    models.When(models.Q(items__current_quantity__gt=0), models.F('items__id')),
                    default=None
                ), distinct=True),
            unit_sizes=pg_agg.StringAgg(
                'items__unit_size', ', ', default=models.Value(''), ordering='items__unit_size', distinct=True),
        )
        # TODO: might not be the right place, but an average price would be nice.
        qs = qs.order_by('name', 'created')
        return qs


class CommonItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("primary name", max_length=1024, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    location = models.ForeignKey(
        "inventory.Location", on_delete=models.CASCADE, null=True, blank=True, related_name='common_items')
    category = models.ForeignKey(
        "inventory.Category", on_delete=models.CASCADE, null=True, blank=True, related_name='common_items')

    objects = CommonItemManager()
    # TODO: link to vendor common items
    # TODO: unit of measure
    # TODO: closed quantity flag

    class Meta:
        ordering = ('name', 'created', )

    def __str__(self):
        # TODO: this habit of putting querysets in the __str__ is causing all kinds of db access unnecessarily.
        # when serializing something that shows the common_item as a string, it runs this query for each item.
        other_names = "', '".join(self.other_names.all().values_list('name', flat=True))
        if other_names:
            return f"{self.name} a.k.a. '{other_names}'"
        return self.name

    def make_item(self, unit_size, unit_cost):
        # Create a 0 quantity item from this common item.
        return self.items.create(unit_size=unit_size, unit_cost=unit_cost, location=self.location)

# ? items
#     - provides a listing of all items which can be used as a dictionary/lookup table
#     names are basic - not vendor specific
#     link to vendor/donation items to provide a way to automatically link incoming items to inventory items.
#     unit of measure
#         uom could be a specific size bag if the count is of unopened containers.
#         uom could be a volume, weight, or count.  ex: liquid, powder, or egg.
#     closed quantity - flag to tell if this item should count only unopened containers or any partial quantities.
#         this should be set as a default to whatever is most common.  maybe a setting or a db value?


class CommonItemOtherName(models.Model):
    """
    Alternate names for a common item.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("alternate name", max_length=1024, null=False, blank=False)
    common_item = models.ForeignKey(CommonItem, on_delete=models.CASCADE, related_name="other_names")

    def __str__(self):
        return f"({self.common_item.name}) {self.name}"
