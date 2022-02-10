from django.db import models
from django.views import generic
from django.utils import timezone

from dateutil import relativedelta

from incoming import models as inc_models
import scrap


class IncomingGroupListView(generic.TemplateView):
    template_name = "incoming/incoming_group_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        limit_to = scrap.first_of_month() - relativedelta.relativedelta(months=6)
        data = inc_models.IncomingItemGroup.objects.list_groups_by_converted_state()
        kwargs.update(data)
        return kwargs
