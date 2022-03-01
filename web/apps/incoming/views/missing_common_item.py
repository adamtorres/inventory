from django import urls
from django.views import generic

from incoming import models as inc_models
from inventory import models as inv_models


class MissingCommonItemView(generic.TemplateView):
    template_name = "incoming/missing_common_item.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
