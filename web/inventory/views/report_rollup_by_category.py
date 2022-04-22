from django import urls, shortcuts
from django.views import generic

from inventory import models as inv_models, reports as inv_reports
from scrap import views as sc_views, utils as sc_utils


class TimePeriodView:
    default_time_period = "last_three_months"
    relative_time_periods = {
        "last_three_months": {"name": "Last 3 months", "months": 3},
        "last_six_months": {"name": "Last 6 months", "months": 6},
        "last_twelve_months": {"name": "Last 12 months", "months": 12},
    }
    reverse_url_with_time_period = ""

    def __init__(self):
        super().__init__()
        for k in self.relative_time_periods.keys():
            if "months" in self.relative_time_periods[k]:
                time_period = sc_utils.last_months(self.relative_time_periods[k]["months"])
                self.relative_time_periods[k].update(time_period)

    def get(self, request, *args, **kwargs):
        # Not calling super() as the only lines in TemplateView's get() are get_context_data and render_to_response.
        context = self.get_context_data(**kwargs)
        if context.get('redirect_to'):
            return shortcuts.redirect(context.get('redirect_to'))
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_period'] = kwargs.get('time_period') or 'redirect to first time period'
        context['time_periods'] = {}
        context['time_periods'].update(self.relative_time_periods)
        context['time_periods'].update(sc_utils.recent_quarters())

        context['selected_time_period'] = context['time_periods'].get(context['time_period'])
        if not context['selected_time_period']:
            context['redirect_to'] = urls.reverse(
                self.reverse_url_with_time_period, kwargs={"time_period": self.default_time_period})
        return context


class ReportRollupByCategoryView(TimePeriodView, sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/report_rollup_by_category.html"
    on_page_title = "Rollup By Category"
    reverse_url_with_time_period = 'inventory:report_rollup_by_category_time_period'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'redirect_to' in context:
            return context
        context['rollup_by_category'] = inv_reports.get_rollup_by_category_data(
            context['selected_time_period']['start__gte'], context['selected_time_period']['end__lte'])
        return context
