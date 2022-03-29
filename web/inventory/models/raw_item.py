from django.contrib.postgres import aggregates as pg_agg
from django.db import models
from django.db.models import functions

from scrap import models as sc_models
from scrap.models import fields as sc_fields
from . import mixins as inv_mixins
from .source import Source


class RawItemManager(inv_mixins.GetsManagerMixin, sc_models.WideFilterManagerMixin, models.Manager):
    def get_item_filter(self, qs=None):
        qs = (qs or self)
        i_filter = models.Q()
        distinct_qs = qs.order_by('source', 'name')
        distinct_qs = distinct_qs.distinct('source', 'name')
        for ri in distinct_qs:
            i_filter |= ri.get_item_filter()
        return i_filter

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('common_item_name_group', 'source', 'category')
        return qs

    def items(self, qs=None, only_new=False):
        fields = ['source', 'name']
        qs = (qs or self).values(*fields)
        qs = qs.distinct(*fields)
        if only_new:
            qs = qs.exclude(item__isnull=False)
        qs = qs.order_by(*fields)
        source_cache = {obj.id: obj for obj in Source.objects.all()}
        qs_list = []
        for item in qs:
            qs_list.append({
                "source": source_cache[item["source"]],
                "name": item["name"],
            })
        return qs_list

    def missing_common_item_name(self):
        return self.exclude(common_item_name_group__isnull=False)


class RawItemReportManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('common_item_name_group', 'source', 'category')
        return qs

    def console_missing_common_item_name(self):
        qs = self.model.objects.missing_common_item_name().values('name', 'category__name').annotate(
            unit_sizes=pg_agg.ArrayAgg(
                functions.Concat(
                    functions.Cast('pack_quantity', models.IntegerField()), models.Value('x '), 'unit_size',
                    output_field=models.CharField()), distinct=True),
            count=models.Count('raw_incoming_items__id'),
        )
        for name in qs:
            print(f"{name['count']}\t{name['category__name']}\t{', '.join(name['unit_sizes'])}\t{name['name']}")


class RawItem(inv_mixins.GetsModelMixin, sc_models.WideFilterModelMixin, sc_models.DatedModel):
    wide_filter_fields = {
        'name': [
            'name', 'better_name', 'common_item_name_group__uncommon_item_names',
            'common_item_name_group__names__name'],
        'category': ['category__name', 'raw_incoming_items__category'],
        # 'department': ['raw_incoming_items__department', 'raw_incoming_items__department_obj__name'],
        'comment': ['item_comment', 'raw_incoming_items__item_comment', 'raw_incoming_items__order_comment'],
        'unit_size': ['unit_size', 'raw_incoming_items__unit_size'],
        'quantity': [
            'pack_quantity', 'raw_incoming_items__pack_quantity', 'raw_incoming_items__ordered_quantity',
            'raw_incoming_items__delivered_quantity'],
        'code': ['item_code', 'extra_code', 'raw_incoming_items__item_code', 'raw_incoming_items__extra_code'],
    }

    source = models.ForeignKey(
        "inventory.Source", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items")
    # TODO: first/last order dates, avg price, last price

    name = sc_fields.CharField(blank=False)
    unit_size = sc_fields.CharField()
    pack_quantity = sc_fields.DecimalField(default=1)
    unit_quantity = models.IntegerField(default=1, help_text="For unit_size=ct/dz, this converts that to a number")

    category = models.ForeignKey(
        "inventory.Category", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items")
    better_name = sc_fields.CharField(help_text="Less cryptic item name")
    item_code = sc_fields.CharField()
    extra_code = sc_fields.CharField()
    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")

    # Primary common item name group
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.SET_NULL, related_name="raw_items",
        related_query_name="raw_items", null=True, blank=True)
    item = models.ForeignKey(
        "inventory.Item", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items",
        null=True, blank=True
    )

    objects = RawItemManager()
    reports = RawItemReportManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                'source', 'name', 'unit_size', 'pack_quantity', name='source-name-unit_size-pack_quantity'),
        ]

    def __str__(self):
        tmp = f"{self.source}, {self.name}"
        if self.pack_quantity != 1:
            tmp += f", {self.pack_quantity}"
        if self.unit_size:
            tmp += f", {self.unit_size}"
        return tmp

    def get_item_filter(self):
        """
        Returns a filter that can be used to find this item in Item before the foreign key is set.
        """
        return models.Q(source=self.source, name=self.name)

    def get_raw_item_filter(self):
        """
        Returns a filter that can be used to find this item in RawIncomingItem before the foreign key is set.
        """
        return models.Q(
            source_obj=self.source, name=self.name, unit_size=self.unit_size, pack_quantity=self.pack_quantity)
