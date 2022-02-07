from django.views import generic

from inventory import models as inv_models


class UsageListView(generic.TemplateView):
    """
    Goal: have a listing of usages showing total costs and if they've been made into a change and applied.
    """
    # template_name = "inventory/usage_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs
