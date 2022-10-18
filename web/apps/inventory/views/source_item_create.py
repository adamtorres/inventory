import logging

from django import urls
from django.views import generic

from inventory import forms as inv_forms, models as inv_models


logger = logging.getLogger(__name__)


class SourceItemCreateView(generic.FormView):
    template_name = "inventory/sourceitem_create.html"
    form_class = inv_forms.SourceItemCreateLineItemModelFormSet
    prefix = "lineitemform"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["line_item_formset"] = context["form"]
        if self.request.method == 'POST':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm(self.request.POST)
        if self.request.method == 'GET':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm()
        return context

    def get_success_url(self):
        return urls.reverse('inventory:sourceitem_search')

    def form_valid(self, form):
        instances = form.save(commit=False)
        for instance in instances:
            if (
                    instance.pack_cost and instance.pack_quantity and instance.delivered_quantity
                    and not instance.extended_cost):
                if instance.total_weight:
                    instance.extended_cost = instance.pack_cost * instance.total_weight
                    logger.debug(f"{instance.extended_cost!r} = {instance.pack_cost!r} * {instance.total_weight}")
                else:
                    instance.extended_cost = instance.pack_cost * instance.delivered_quantity
                    logger.debug(f"{instance.extended_cost!r} = {instance.pack_cost!r} * {instance.delivered_quantity}")
        form.save()
        return super().form_valid(form)
