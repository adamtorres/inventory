import requests

from django import urls
from django.views import generic

from scrap import views as sc_views
from .. import models as inv_models, serializers as inv_serializers
from .api_raw_incoming_order import RawIncomingOrderFilter


class ItemPriceOverTimeView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/item_price_over_time.html"
    on_page_title = "Item Price Over Time"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_report_itempriceovertime"))
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return context
        context['itempriceovertime'] = resp.json()
        return context
