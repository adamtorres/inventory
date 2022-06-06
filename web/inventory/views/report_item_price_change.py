from dateutil import parser
import requests

from django import urls
from django.views import generic

from scrap import views as sc_views
from .. import models as inv_models, serializers as inv_serializers
from .api_raw_incoming_order import RawIncomingOrderFilter


class ReportItemPriceChangeView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/item_price_change.html"
    on_page_title = "Item Price Change"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_report_itempricechange"))
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return context
        context['itempricechange'] = resp.json()
        # The date formatting in the template does not work with the date strings as returned by the api.
        context['itempricechange']['settings']['start_date'] = parser.parse(
            context['itempricechange']['settings']['start_date'])
        context['itempricechange']['settings']['end_date'] = parser.parse(
            context['itempricechange']['settings']['end_date'])

        context['itempricechange']['stats']['min_date'] = parser.parse(
            context['itempricechange']['stats']['min_date'])
        context['itempricechange']['stats']['max_date'] = parser.parse(
            context['itempricechange']['stats']['max_date'])
        return context
