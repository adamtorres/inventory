from django.views import generic

from conversion import models as con_models


class ConversionReportView(generic.TemplateView):
    template_name = "conversion/conversion_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['conversions'] = con_models.Measure.objects.avg_report()
        return context
