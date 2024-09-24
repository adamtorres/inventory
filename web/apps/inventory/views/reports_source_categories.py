from django.views import generic

from inventory import reports as inv_reports


class ReportsSourceCategoriesView(generic.TemplateView):
    template_name = "inventory/reports_source_categories.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['source_categories'] = inv_reports.SourceCategories.run()
        return context
