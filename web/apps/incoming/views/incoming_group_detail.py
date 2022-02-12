from django.views.generic import DetailView
from incoming import models as inc_models


class IncomingGroupDetailView(DetailView):
    model = inc_models.IncomingItemGroup

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('source', 'items', 'items__item', 'items__item__common_item')
        return qs
