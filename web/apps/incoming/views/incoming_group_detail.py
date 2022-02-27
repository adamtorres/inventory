from django.views.generic import DetailView
from incoming import models as inc_models


class IncomingGroupDetailView(DetailView):
    model = inc_models.IncomingItemGroup

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['on_page_title'] = "Item Group Detail"
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('source', 'items', 'items__item', 'items__item__common_item')
        return qs
