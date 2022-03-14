import requests

from django import urls
from django.views import generic

from .. import models as inv_models, serializers as inv_serializers
from .api_raw_incoming_item import APIRawIncomingItemListView


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
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_rawincomingitem_list"))
        resp = requests.get(api_url, params=api_get_data)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        # TODO: Is it necessary to run the json through the serializer to get objects?  Using the dicts seems to work.
        # context['object_list'] = inv_serializers.RawIncomingItemSerializer(api_return_data['results'], many=True).data
        context['object_list'] = api_return_data['results']
        return context
