from django import urls
from django.views import generic

from incoming import models as inc_models


class IncomingGroupItemLookupView(generic.TemplateView):
    template_name = "incoming/incoming_group_item_lookup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['on_page_title'] = "Item Lookup"
        return context
