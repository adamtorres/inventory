from django.contrib.postgres import fields as pg_fields, aggregates as pg_agg
from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class CommonItemNameGroupManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('name')
        return qs

    def with_in_stock_quantities(self, qs=None, by_unit_size=False):
        """
        Returns a QuerySet of dict showing counts and totals by name/unit_size.
        {
            'id': UUID,
            'category_str': 'meats',
            'name_str': 'beef top round',
            'unit_size': '7-11#',
            'sources': ['sysco'],
            'orders': 8,
            'total_pack_quantity': Decimal('32.0000')
        }
        """
        # TODO: I don't like name_str.  The orm didn't let me shadow the name field.  Probably a way around it.
        qs = (qs or self).values(
            'id',
            name_str=models.F('name__name'),
            category_str=models.F('category__name'),
            unit_size=models.F('raw_items__unit_size'))
        qs = qs.annotate(
            item_in_stock_ids=pg_agg.ArrayAgg(
                models.F('raw_items__raw_incoming_items__in_stock__id'), distinct=True,
            ),
            sources=pg_agg.ArrayAgg(
                models.F('raw_items__source__name'), distinct=True, ordering=['raw_items__source__name']),
            order_count=models.Count(
                models.Case(
                    models.When(
                        models.Q(raw_items__raw_incoming_items__in_stock__remaining_pack_quantity__gt=0),
                        then=models.F('raw_items__raw_incoming_items__in_stock__id')),
                    default=None
                ),
                distinct=True),
            pack_quantity=models.Sum('raw_items__raw_incoming_items__in_stock__remaining_pack_quantity')
        ).order_by('category_str', 'name_str', 'unit_size')
        if by_unit_size:
            return qs
        return sc_utils.list_group(
            qs, ["id", "category_str", "name_str"], group_name="quantities", sub_group_fields="unit_size",
            sum_fields=["order_count", "pack_quantity"], set_fields=['sources', 'item_in_stock_ids'])

    def search_multiple_names(self, terms):
        """
        terms in this case is a list of names.  If terms is a str, will be treated as a list of one item.
        This is for when wanting a single QuerySet from searching for "ground beef" and "orange juice".
        """
        if isinstance(terms, str):
            terms = [terms]
        q = models.Q()
        for term in terms:
            q |= self.search_name_filter(term)
        qs = self.filter(id__in=self.filter(q).values('id').distinct('id'))
        return qs

    def search_names(self, terms):
        # Because the terms could match to different names__name values, the results could contain dupes.
        # Grabbing the ids from that set and using them to drive a "clean" queryset removes the dupes and also makes
        # it so users of this function don't have to deal with ".distinct()".
        q = self.search_name_filter(terms)
        qs = self.filter(id__in=self.filter(q).values('id').distinct('id'))
        return qs

    def search_name_filter(self, terms):
        if isinstance(terms, str):
            terms = terms.split()
        q = models.Q()
        fields = ['name__name', 'uncommon_item_names', 'names__name']
        for field in fields:
            term_q = models.Q()
            for term in terms:
                kwarg = {f"{field}__icontains": term}
                term_q &= models.Q(**kwarg)
            q |= term_q
        return q


class CommonItemNameGroup(sc_models.UUIDModel):
    # 'name' is the primary name of the group (nonstick spray).
    # Use 'names' to get all common names (cooking spray, pan spray, nonstick spray, pam).
    name = models.ForeignKey(
        "inventory.CommonItemName", on_delete=models.SET_NULL, null=True, related_name="primary_groups")
    category = models.ForeignKey("inventory.Category", on_delete=models.SET_NULL, null=True)

    uncommon_item_names = pg_fields.ArrayField(
        models.CharField(max_length=1024, null=False, blank=False), null=False, blank=True, default=list)

    objects = CommonItemNameGroupManager()

    def __str__(self):
        if self.name:
            return self.name.name
        return f"Unnamed CommonItemNameGroup({self.id})"


class CommonItemName(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False)
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.CASCADE, related_name="names", related_query_name="names",
        null=True
    )

    def __str__(self):
        return self.name
