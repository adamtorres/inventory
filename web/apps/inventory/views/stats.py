from django.views import generic

from inventory import models as inv_models


class SourceItemStatsView(generic.TemplateView):
    template_name = "inventory/sourceitem_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = inv_models.SourceItem.objects.stats()
        return context
