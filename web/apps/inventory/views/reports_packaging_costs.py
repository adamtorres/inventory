from django.views import generic

from inventory import reports as inv_reports


class ReportsPackagingCostsView(generic.TemplateView):
    template_name = "inventory/reports_packaging_costs.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['packaging_costs'] = inv_reports.PackagingCosts.run()
        return context
