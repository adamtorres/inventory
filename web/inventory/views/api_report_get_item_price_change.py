from django.db import models
from rest_framework import renderers, response, views, generics

from scrap import utils as sc_utils
from .. import models as inv_models, serializers as inv_serializers, reports as inv_reports


class APIItemPriceChangeView(views.APIView):
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
        # highest_qs = inv_models.RawIncomingItem.reports.highest_spending_items(months=months)
        # highest_filter = highest_qs.values_list('rawitem_obj_id', flat=True)
        # selected_item_filter = models.Q(rawitem_obj_id__in=highest_filter)
        # selected_item_filter = models.Q(rawitem_obj__common_item_name_group__name__name__in=common_item_names)
        data = inv_reports.get_item_price_change_report(*sc_utils.get_monthly_date_range(months), common_item_names)
        return response.Response(data)
