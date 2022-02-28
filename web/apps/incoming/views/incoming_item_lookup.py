from django import urls
from django.views import generic

from incoming import models as inc_models
from inventory import models as inv_models


class IncomingGroupItemLookupView(generic.TemplateView):
    template_name = "incoming/incoming_group_item_lookup.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['on_page_title'] = "Item Lookup"
        if "item_id" in self.request.GET:
            context["item_id"] = self.request.GET["item_id"]
        context['sources'] = inc_models.Source.objects.all().order_by('name')
        context['departments'] = inv_models.Department.objects.all().order_by('name')
        return context
