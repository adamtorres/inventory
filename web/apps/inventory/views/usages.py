from django.views import generic

from inventory import models as inv_models


class UsageView(generic.TemplateView):
    """
    Goal: have a listing of usages showing total costs and if they've been made into a change and applied.
    """
    # template_name = "inventory/usage_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs


class UsageReportCreateView(generic.CreateView):
    model = inv_models.Usage
    fields = ('who', 'action_date', )


class UsageReportDetailView(generic.DetailView):
    model = inv_models.Usage


class UsageReportListView(generic.ListView):
    model = inv_models.Usage


class UsageReportEditView(generic.UpdateView):
    model = inv_models.Usage
    fields = ('who', 'action_date', )
