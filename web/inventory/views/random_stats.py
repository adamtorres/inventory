import collections

from django import urls
from django.db import models
from django.views import generic

from inventory import models as inv_models
from scrap import views as sc_views


class RandomStatsView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/random_stats.html"
    on_page_title = "Random stats"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['units'] = self.get_units()
        context['models_counts'] = self.get_model_counts()
        context['items_by_state'] = self.get_item_counts_by_current_state()
        return context

    def get_item_counts_by_current_state(self):
        counts_by_state = []
        for counts in inv_models.RawIncomingItem.reports.group_by_current_state().order_by('state'):
            counts_by_state.append((counts["state__value"], counts["state__name"], counts["count"]))
        return counts_by_state

    def get_model_counts(self):
        counts = inv_models.get_model_counts()
        return [(k, counts[k]) for k in sorted(counts.keys())]

    def get_units(self):
        """
        returns a dict with model name as keys and list of (unit, count) tuples.
        """
        units = {}
        for model in [inv_models.RawItem, inv_models.RawIncomingItem]:
            units[model._meta.object_name] = model.objects.get_possible_unit_counts(as_list_of_tuples=True)
        return units
