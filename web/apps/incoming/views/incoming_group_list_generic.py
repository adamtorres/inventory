from django.views.generic import ListView

from incoming import models as inc_models


class IncomingGroupView(ListView):
    """
    Using the ListView to show the IIGs instead of manually making everthing.
    """
    model = inc_models.IncomingItemGroup

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('source', 'items__item__common_item')
        return qs.order_by('-action_date')

    def get_context_data(self, *args, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        return context
