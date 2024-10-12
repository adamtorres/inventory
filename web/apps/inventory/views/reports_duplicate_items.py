from django.views import generic

from scrap import utils

from inventory import reports as inv_reports


class ReportsDuplicateItemsView(generic.TemplateView):
    template_name = "inventory/reports_duplicate_items.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['duplicate_items'] = inv_reports.DuplicateItems.run()
        return context
