from inventory import models as inv_models, serializers as inv_serializers

from scrap import views as sc_views


class RawIncomingItemWideFilterView(sc_views.WideFilterView):
    model = inv_models.RawIncomingItem
    serializer = inv_serializers.RawIncomingItemFlatSerializer
    prefetch_fields = [
        'source_obj', 'category_obj', 'department_obj', 'rawitem_obj',
        'rawitem_obj__category', 'rawitem_obj__source', 'rawitem_obj__common_item_name_group',
        'rawitem_obj__common_item_name_group__category', 'rawitem_obj__common_item_name_group__name'
    ]


class RawItemWideFilterView(sc_views.WideFilterView):
    model = inv_models.RawItem
    serializer = inv_serializers.RawItemSerializer
    prefetch_fields = [
        'category', 'source', 'common_item_name_group',
        'common_item_name_group__category', 'common_item_name_group__name'
    ]