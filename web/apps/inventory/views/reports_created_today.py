from django.views import generic

from scrap import utils

from inventory import reports as inv_reports


class ReportsCreatedTodayView(generic.TemplateView):
    template_name = "inventory/reports_created_today.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # pass_along = ["source_id", "source", "order_number", "delivered_date", "general_search"]
        # for get_param in pass_along:
        #     if get_param in self.request.GET:
        #         context[f"pass_in_{get_param.replace('-', '_')}"] = self.request.GET[get_param]

        context['created_today'] = inv_reports.CreatedToday.run()
        return context
