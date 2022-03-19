from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class RawItemManager(sc_models.WideFilterManagerMixin, models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related('common_item_name_group', 'source', 'category')
        return qs

    def missing_common_item_name(self):
        return self.exclude(common_item_name_group__isnull=False)


class RawItem(sc_models.WideFilterModelMixin, sc_models.DatedModel):
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
    pack_quantity = sc_fields.DecimalField()
    unit_quantity = models.IntegerField(default=1, help_text="For unit_size=ct/dz, this converts that to a number")

    category = models.ForeignKey(
        "inventory.Category", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items")
    better_name = sc_fields.CharField(help_text="Less cryptic item name")
    item_code = sc_fields.CharField()
    extra_code = sc_fields.CharField()
    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")

    # Primary common item name group
    common_item_name_group = models.ForeignKey(
        "inventory.CommonItemNameGroup", on_delete=models.SET_NULL, null=True, blank=True)

    objects = RawItemManager()

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

    def get_raw_item_filter(self):
        """
        Returns a filter that can be used to find this item in RawIncomingItem before the foreign key is set.
        """
        return models.Q(
            source_obj=self.source, name=self.name, unit_size=self.unit_size, pack_quantity=self.pack_quantity)
