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
        selected_item_filter = models.Q(rawitem_obj__common_item_name_group__name__name__in=common_item_names)
        data = inv_models.RawIncomingItem.reports.routinely_ordered_items(
            months=6, selected_item_filter=selected_item_filter)
        return response.Response(data)
