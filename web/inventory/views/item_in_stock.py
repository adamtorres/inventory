import requests

from django import urls
from django.views import generic

from scrap import views as sc_views


class ItemInStockListView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/item_in_stock_list.html"
    on_page_title = "Items In Stock"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = []
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_commonitemwithinstockquantities_list"))
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        context['object_list'] = api_return_data
        return context
