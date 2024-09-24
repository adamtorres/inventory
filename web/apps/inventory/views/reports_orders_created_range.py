from django.views import generic

from inventory import reports as inv_reports


class ReportsOrdersCreatedRangeView(generic.TemplateView):
    template_name = "inventory/reports_orders_created_range.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders_created_range'] = inv_reports.OrdersCreatedRange.run()
        return context
