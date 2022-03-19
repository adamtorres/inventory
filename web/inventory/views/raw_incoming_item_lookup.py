from django import urls
from django.views import generic

from inventory import models as inv_models
from scrap import views as sc_views


class RawIncomingItemLookupView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/rawincomingitem_lookup.html"
    on_page_title = "Raw Incoming Item Lookup"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "item_id" in self.request.GET:
            context["item_id"] = self.request.GET["item_id"]
        context['sources'] = inv_models.Source.objects.all().order_by('name')
        context['categories'] = inv_models.Category.objects.all().order_by('name')
        context['departments'] = inv_models.Department.objects.all().order_by('name')
        return context
