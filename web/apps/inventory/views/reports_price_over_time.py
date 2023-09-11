from django.views import generic

from scrap import utils

from inventory import models as inv_models, reports as inv_reports


class ReportsPriceOverTimeView(generic.TemplateView):
    template_name = "inventory/reports_price_over_time.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        viable_search_criteria = inv_models.SearchCriteria.objects.exclude(name__istartswith="(issues)")
        context["report_names"] = viable_search_criteria.values('name', 'url_slug')
        return context
