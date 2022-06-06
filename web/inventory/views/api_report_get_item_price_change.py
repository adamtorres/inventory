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
            "large eggs", "eggs",
            'mixed vegetables', 'california vegetable blend', 'scandinavian vegetable blend', '5 way vegetable mix', 'fajita vegetables',
            'diced mixed fruit', 'fruit cocktail', 'sliced peaches', 'diced pears', 'apple slices', 'crushed pineapple', 'pineapple chunks', 'pineapple slices', 'pineapple tidbits',
            'country fried beef fritter', 'beef top round', 'pickled beet slices',
            'grape juice', 'apple juice', 'orange juice', 'cranberry cocktail juice',
            'center cut pork chop boneless', 'center cut pork loin boneless', 'center cut pork loin boneless strap off', 'pork loin boneless rolled tied', 'center cut pork loin boneless strap on',
            'chicken cordon bleu', 'frozen chicken breast', 'breaded chicken breast patty precooked'
        ]
        months = 12
        report_settings = inv_models.ReportSetting.objects.for_report('item_price_change')
        months = report_settings.get('months', months)
        month_range = sc_utils.get_monthly_date_range(months)
        common_item_names = report_settings.get('items', common_item_names)
        # highest_qs = inv_models.RawIncomingItem.reports.highest_spending_items(months=months)
        # highest_filter = highest_qs.values_list('rawitem_obj_id', flat=True)
        # selected_item_filter = models.Q(rawitem_obj_id__in=highest_filter)
        # selected_item_filter = models.Q(rawitem_obj__common_item_name_group__name__name__in=common_item_names)
        data = inv_reports.get_item_price_change_report(*month_range, common_item_names)
        data['settings']['months'] = months
        return response.Response(data)
