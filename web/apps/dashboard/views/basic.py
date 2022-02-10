from django.views import generic

from incoming import models as inc_models
from inventory import models as inv_models


class BasicDashboardView(generic.TemplateView):
    template_name = "dashboard/basic.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["most_recent_order_per_source"] = inc_models.most_recent_order_per_source()
        kwargs["location_summary"] = inv_models.Location.objects.get_cost()
        kwargs["inventory_changes_by_month"] = inv_models.Change.objects.summary_relative_by_month(12)
        return kwargs
