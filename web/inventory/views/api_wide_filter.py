from django.db import models

from inventory import models as inv_models, serializers as inv_serializers
from scrap import views as sc_views
from scrap.models import fields as sc_fields


class CommonItemNameGroupWideFilterView(sc_views.WideFilterView):
    # model = inv_models.CommonItemNameGroup
    # serializer = inv_serializers.ItemWithInStockQuantitiesSerializer
    model = inv_models.CommonItemNameGroup
    serializer = inv_serializers.CommonItemNameGroupWideFilterSerializer
    order_fields = ['name__name']
    prefetch_fields = [
        'names',
        'raw_items', 'raw_items__category', 'raw_items__raw_incoming_items',
        'raw_items__raw_incoming_items__source_obj'
    ]

    def filter_qs(self, search_terms):
        filtered_qs = super().filter_qs(search_terms)
        # TODO: Would be nice if this returned counts by unit_size in some array/dict
        qs = self.get_queryset().filter(id__in=filtered_qs).annotate(
            order_count=models.Count('raw_items__raw_incoming_items__id'),
            remaining_price=models.Sum(
                models.F('raw_items__raw_incoming_items__in_stock__unit_price') * models.F('raw_items__raw_incoming_items__in_stock__remaining_unit_quantity')
                + models.F('raw_items__raw_incoming_items__in_stock__count_price') * models.F('raw_items__raw_incoming_items__in_stock__remaining_count_quantity'),
                output_field=sc_fields.MoneyField()
            )
        )
        return qs

    def get_queryset(self):
        # Only care about items with some usable quantities
        return super().get_queryset().select_related('name').filter(
            models.Q(raw_items__raw_incoming_items__in_stock__remaining_unit_quantity__gt=0) |
            models.Q(raw_items__raw_incoming_items__in_stock__remaining_count_quantity__gt=0)
        )


class RawIncomingItemWideFilterView(sc_views.WideFilterView):
    model = inv_models.RawIncomingItem
    serializer = inv_serializers.RawIncomingItemFlatSerializer
    order_fields = ['-delivery_date', 'source', 'order_number', 'line_item_position']
    prefetch_fields = [
        'source_obj', 'category_obj', 'department_obj', 'rawitem_obj',
        'rawitem_obj__category', 'rawitem_obj__source', 'rawitem_obj__common_item_name_group',
        'rawitem_obj__common_item_name_group__category', 'rawitem_obj__common_item_name_group__name'
    ]


class RawItemWideFilterView(sc_views.WideFilterView):
    model = inv_models.RawItem
    serializer = inv_serializers.RawItemSerializer
    order_fields = ['name', 'source__name', 'unit_size', 'pack_quantity']
    prefetch_fields = [
        'category', 'source', 'common_item_name_group',
        'common_item_name_group__category', 'common_item_name_group__name'
    ]