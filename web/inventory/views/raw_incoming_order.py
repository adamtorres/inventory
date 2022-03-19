import requests

from django import urls
from django.views import generic

from scrap import views as sc_views
from .. import models as inv_models, serializers as inv_serializers
from .api_raw_incoming_order import RawIncomingOrderFilter


class RawIncomingOrderDetailView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/rawincomingorder_detail.html"
    on_page_title = "Raw Incoming Order Detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"RawIncomingOrderDetailView.get_context_data: {kwargs}")
        # api_get_data['format'] = 'json'
        relative_url = urls.reverse("inventory:api_rawincomingorder_detail", kwargs={'pk': kwargs['pk']})
        api_url = self.request.build_absolute_uri(relative_url)
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        context['object'] = api_return_data
        return context


class RawIncomingOrderListView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/rawincomingorder_list.html"
    on_page_title = "Raw Incoming Order List"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = []
        # copy any GET args for the api except 'format' as that will be forced to json
        api_get_data = {k: v for k, v in self.request.GET.items() if k in RawIncomingOrderFilter.Meta.fields}
        if "reset" in self.request.GET:
            self.request.session["order_filters"] = {}
        if not api_get_data:
            api_get_data = self.request.session.get("order_filters") or {}
        self.request.session["order_filters"] = api_get_data.copy()
        api_get_data['format'] = 'json'
        api_get_data['paging'] = 'off'
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_rawincomingorder_list"))
        resp = requests.get(api_url, params=api_get_data)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        # TODO: Is it necessary to run the json through the serializer to get objects?  Using the dicts seems to work.
        # context['object_list'] = inv_serializers.RawIncomingOrderSerializer(api_return_data['results'], many=True).data
        if api_get_data['paging'] == 'off':
            # Unpaged results are not in an outer dict
            context['object_list'] = api_return_data
        else:
            context['object_list'] = api_return_data['results']
        return context

