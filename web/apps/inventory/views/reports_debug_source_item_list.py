from django.views import generic

from scrap import utils

from inventory import reports as inv_reports


class ReportsDebugSourceItemListView(generic.TemplateView):
    template_name = "inventory/reports_debug_source_item_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debug_source_item_list'] = inv_reports.DebugSourceItemList.run()
        return context
