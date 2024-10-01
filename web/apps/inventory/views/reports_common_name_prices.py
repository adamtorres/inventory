from django.views import generic

from scrap import utils

from inventory import reports as inv_reports


class ReportsCommonNamePricesView(generic.TemplateView):
    template_name = "inventory/reports_common_name_prices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_name_prices'] = inv_reports.CommonNamePrices.run()
        return context
