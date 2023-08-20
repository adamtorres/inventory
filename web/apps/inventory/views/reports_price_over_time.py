from django.views import generic

from scrap import utils

from inventory import models as inv_models, reports as inv_reports


class ReportsPriceOverTimeView(generic.TemplateView):
    template_name = "inventory/reports_price_over_time.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
