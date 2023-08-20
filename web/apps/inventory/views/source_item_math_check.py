import logging

from django.views import generic

from inventory import models as inv_models


logger = logging.getLogger(__name__)


class SourceItemMathCheckView(generic.TemplateView):
    template_name = "inventory/sourceitem_math_check.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['saved_searches'] = inv_models.SearchCriteria.objects.all()
        return context
