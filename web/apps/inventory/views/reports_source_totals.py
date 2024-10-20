from django.views import generic

from inventory import reports as inv_reports


class ReportsSourceTotalsView(generic.TemplateView):
    template_name = "inventory/reports_source_totals.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source_totals'] = inv_reports.SourceTotals.run()
        return context
