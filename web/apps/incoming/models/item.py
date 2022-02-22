from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid

import scrap


class ItemManager(models.Manager):
    def available_items(self, source=None):
        qs = self.exclude(discontinued=True).select_related('source')
        if source is not None:
            # Using "if source" seems to execute the query on the database.
            if isinstance(source, models.QuerySet):
                qs = qs.filter(source__in=source)
            else:
                qs = qs.filter(source=source)
        return qs

    def autocomplete_search(self, terms, sources=None):
        """
        Provided a single or list of terms, search item names, common names, and other names for the terms.  Return a
        queryset of the found items.  Optionally filter on source(s) when provided with a single or list of UUIDs.

        Args:
            terms: single string or list of strings.
            sources: list of UUIDs as strings

        Returns:
            queryset with the result.
        """
        # TODO: Should this be expanded to handle multi-term phrases?  as in "ham meat" would not return "hamburger bun"
        # TODO: returning duplicates for "stick" - ids are duplicated, at least.
        if not terms:
            return self.none()
        if isinstance(terms, str):
            terms = [terms]

        term_q = models.Q()

        for term in terms:
            term_q = (
                term_q | models.Q(name__icontains=term) | models.Q(common_item__name__icontains=term) |
                models.Q(common_item__other_names__name__icontains=term))
        source_q = models.Q()
        if sources and sources != ['']:
            print(f"sources before = {sources!r}")
            if isinstance(sources, (str, uuid.UUID)):
                print("sources is a singular str or uuid.   Making it a list.")
                sources = [sources]
            print(f"sources after = {sources!r}, type = {type(sources)}")
            for source in sources:
                source_q = source_q | models.Q(source__id=source)
        return self.prefetch_related(
            'common_item', 'common_item__other_names', 'source').filter(term_q, source_q).order_by('name')


class Item(models.Model):
    # A unique item needs to be identifier/name/pack_quantity/unit_size
    # 2021-05-27 and 2021-07-29 "5239389" / "SYS CLS extract vanilla imit" / 1 and 6 / 32oz
    # 2021-07-01 and 2021-07-15 "6639553" / "IMP/MCC seasoning steak montreal" / 1 and 6 / 29oz
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey("incoming.Source", on_delete=models.CASCADE, related_name="items")
    identifier = models.CharField(max_length=1024, null=False, blank=True, default='', help_text="code, upc, etc.")
    name = models.CharField("Probably cryptic item name", max_length=1024, null=False, blank=False)
    better_name = models.CharField("Less cryptic item name", max_length=1024, null=False, blank=True, default='')
    common_item = models.ForeignKey(
        "inventory.CommonItem", on_delete=models.CASCADE, related_name="incoming_items", null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    do_not_inventory = models.BooleanField(default=False, null=False, blank=False)
    individual_serving = models.BooleanField(
        default=False, null=False, blank=False, help_text="Is a preportioned single-serving disposable package")

    # Just a helper for reports or drop downs so they are filled with garbage.
    discontinued = models.BooleanField(default=False, null=False, blank=False)

    # A single package can have multiple items.
    pack_quantity = models.DecimalField(max_digits=10, decimal_places=4, null=False, blank=False, default=0)
    unit_size = models.CharField(max_length=1024, null=False, blank=False, default='count')

    # price is not here as the prices change quite often.

    objects = ItemManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['source', 'identifier', 'name', 'pack_quantity', 'unit_size'],
                name='unique_source_id_name_packqty_size')
        ]
    # vendor/donation items
#     - This is not items on an order.  This is just a way to convert between vendor and inventory.
#     - There might be multiple items that are actually the same thing as vendors sometimes change item
#           numbers/descriptions.
#     - names are specific to vendor/donator
#     some kind of link to an inventory item so we can easily convert an incoming item to an inventory item.
#     how to convert between this item's quantity to inventory item's quantity.

# incoming items
#     a complete list of items that come from outside.
#     This is not actual incoming items.  This is a list of names which also link to common items.

    def __str__(self):
        return f"{self.source.name} / {self.item_name}"

    @property
    def item_name(self):
        return f"{scrap.undecimal(self.pack_quantity)}x {self.unit_size}, {self.name}"

    def get_delivered_unit_quantity(self, delivered_quantity):
        # QuantityConversions:
        # unit_size is a count.  int(unit_size [remove suffix]) * pack_quantity * delivered_quantity = total_quantity
        # unit_size is unique to the instance but not a usable.  pack_quantity * delivered_quantity = total_quantity
        # unit_size is constant but not a usable number. pack_quantity * delivered_quantity = total_quantity
        # unit_size is a count/weight but should still be ignored.  pack_quantity * delivered_quantity = total_quantity
        # TODO: quantity conversion currently hard coded to ignore unit_size.  Will need to change if/when doing more
        #  than 'closed package' counting.
        return self.pack_quantity * delivered_quantity
