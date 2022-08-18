from django.views import generic

from inventory import models as inv_models


class SourceItemSearchView(generic.TemplateView):
    template_name = "inventory/sourceitem_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = inv_models.SourceItem.objects.source_names()
        context['categories'] = inv_models.SourceItem.objects.source_categories()
        return context
