import requests

from django import urls
from django.views import generic

from .. import models as inv_models, serializers as inv_serializers


class RawIncomingItemCreateView(generic.CreateView):
    model = inv_models.RawIncomingItem
    fields = [
        "source", "department", "customer_number", "order_number", "po_text", "order_comment", "order_date",
        "delivery_date", "total_price", "total_packs", "line_item_position", "category", "name", "ordered_quantity",
        "delivered_quantity", "item_code", "extra_code", "unit_size", "total_weight", "pack_quantity", "pack_price",
        "pack_tax", "extended_price", "item_comment", "scanned_image_filename", ]


class RawIncomingItemDeleteView(generic.DeleteView):
    model = inv_models.RawIncomingItem

    def get_success_url(self):
        return urls.reverse("inventory:rawincomingitem_list")


class RawIncomingItemDetailView(generic.DetailView):
    model = inv_models.RawIncomingItem


class RawIncomingItemListView(generic.TemplateView):
    template_name = "inventory/rawincomingitem_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = []

        # copy any GET args for the api except 'format' as that will be forced to json
        api_get_data = {k: v for k, v in self.request.GET.items() if k != "format"}
        api_get_data['format'] = 'json'
        api_get_data['paging'] = 'off'
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_rawincomingitem_list"))
        resp = requests.get(api_url, params=api_get_data)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        # TODO: Is it necessary to run the json through the serializer to get objects?  Using the dicts seems to work.
        # context['object_list'] = inv_serializers.RawIncomingItemSerializer(api_return_data['results'], many=True).data
        if api_get_data['paging'] == 'off':
            # Unpaged results are not in an outer dict
            context['object_list'] = api_return_data
        else:
            context['object_list'] = api_return_data['results']
        return context


class RawIncomingItemUpdateView(generic.UpdateView):
    model = inv_models.RawIncomingItem
    fields = [
        "source", "department", "customer_number", "order_number", "po_text", "order_comment", "order_date",
        "delivery_date", "total_price", "total_packs", "line_item_position", "category", "name", "ordered_quantity",
        "delivered_quantity", "item_code", "extra_code", "unit_size", "total_weight", "pack_quantity", "pack_price",
        "pack_tax", "extended_price", "item_comment", "scanned_image_filename", ]
