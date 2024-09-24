from django.views import generic

from scrap import utils

from inventory import reports as inv_reports


class ReportsCreatedTimesLastWeekView(generic.TemplateView):
    template_name = "inventory/reports_created_times_last_week.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['created_last_week'] = inv_reports.CreatedTimesLastWeek.run()
        return context
