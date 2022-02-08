from django.views import generic

from inventory import models as inv_models


class ChangeView(generic.TemplateView):
    template_name = "change/over_time.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['changes'] = inv_models.Change.objects.by_year_month(
            year=kwargs.get('year'), month=kwargs.get('month'))
        return kwargs
