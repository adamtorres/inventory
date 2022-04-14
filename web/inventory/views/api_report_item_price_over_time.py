from django.db import models
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIItemPriceOverTimeView(views.APIView):
    def get(self, request):
        common_item_names = [
            "low fat milk cartons",
            "low fat chocolate milk cartons",
            "chocolate pudding",
            "lemon pudding",
            "nonstick spray",
            "butter",
            "margarine",
            "margarine tubs",
            "cool whip",
            "sour cream",
            "cream cheese",
            "flour",
            "ground beef",
        ]
        months = 6
        highest_qs = inv_models.RawIncomingItem.reports.highest_spending_items(months=months)
        highest_filter = highest_qs.values_list('rawitem_obj_id', flat=True)
        selected_item_filter = models.Q(rawitem_obj_id__in=highest_filter)
        # selected_item_filter = models.Q(rawitem_obj__common_item_name_group__name__name__in=common_item_names)
        data = inv_models.RawIncomingItem.reports.routinely_ordered_items(
            months=months, selected_item_filter=selected_item_filter)
        data['highest'] = []
        for item in highest_qs:
            data['highest'].append({
                'rawitem_id': item['rawitem_obj_id'],
                'common_name': item['rawitem_obj__common_item_name_group__name__name'],
                'category': item['rawitem_obj__category__name'],
                'item_code': item['rawitem_obj__item_code'],
                'unit_size': item['rawitem_obj__unit_size'],
                'total_spent': item['total_spent'],
                'total_unit_quantity': item['total_unit_quantity'],
            })

        return response.Response(data)
