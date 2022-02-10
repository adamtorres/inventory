from django.views import generic

from incoming import models as inc_models


class IncomingGroupListView(generic.TemplateView):
    template_name = "incoming/incoming_group_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["incoming_groups"] = inc_models.IncomingItemGroup.objects.all().select_related('source').order_by('-action_date')
        return kwargs
