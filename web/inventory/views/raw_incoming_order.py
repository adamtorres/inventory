import requests

from django import urls
from django.views import generic

from .. import models as inv_models, serializers as inv_serializers


class RawIncomingOrderListView(generic.TemplateView):
    template_name = "inventory/rawincomingorder_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

