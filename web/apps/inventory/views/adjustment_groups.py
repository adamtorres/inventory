import logging

from django import urls
from django import http
from django.views import generic

from inventory import models as inv_models


class AdjustmentGroupCreateView(generic.CreateView):
    model = inv_models.AdjustmentGroup
    fields = [
        'start_date',
        'end_date',
        'adjustment_type',
        'notes',
    ]

    def get_success_url(self):
        return urls.reverse('inventory:adjustment_group_detail', args=(self.object.id,))


class AdjustmentGroupDetailView(generic.DetailView):
    queryset = inv_models.AdjustmentGroup.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group_totals"] = self.object.calculate_costs()
        return context


class AdjustmentGroupListView(generic.ListView):
    include_closed = False

    def get(self, request, *args, **kwargs):
        self.include_closed = request.GET.get('include_closed', '').lower() == "true"
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['include_closed'] = self.include_closed
        return context

    def get_queryset(self):
        return inv_models.AdjustmentGroup.objects.get_groups(include_closed=self.include_closed)


class AdjustmentGroupUpdateView(generic.UpdateView):
    model = inv_models.AdjustmentGroup
    fields = ["notes", "start_date", "end_date", "open", "adjustment_type",]

    def get_success_url(self):
        return urls.reverse('inventory:adjustment_group_detail', args=(self.object.id,))
