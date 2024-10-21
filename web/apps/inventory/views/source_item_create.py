import logging

from django import urls
from django.views import generic

from scrap import utils as sc_utils

from inventory import forms as inv_forms, models as inv_models


logger = logging.getLogger(__name__)


class SourceItemCreateView(generic.FormView):
    template_name = "inventory/sourceitem_create.html"
    form_class = inv_forms.SourceItemCreateLineItemModelFormSet
    prefix = "lineitemform"

    # These fields are populated during form_valid to allow get_success_url to create the link to the newly saved order.
    source_id = None
    order_number = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["line_item_formset"] = context["form"]
        if self.request.method == 'POST':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm(self.request.POST)
        if self.request.method == 'GET':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm()
        return context

    def get_success_url(self):
        return urls.reverse('inventory:sourceitem_order_items', kwargs={
            'source': self.source_id, 'order_number': self.order_number})

    def form_valid(self, form):
        instances = form.save(commit=False)
        self.source_id = None
        self.order_number = None
        for instance in instances:
            if self.source_id is None:
                self.source_id = instance.source.id
                self.order_number = instance.order_number
            if (
                    instance.pack_cost and instance.pack_quantity and instance.delivered_quantity
                    and not instance.extended_cost):
                instance.adjusted_pack_quantity = instance.pack_quantity
                instance.adjusted_count = instance.unit_quantity
                if instance.unit_size:
                    adjusted_units = sc_utils.split_units(instance.unit_size)
                    instance.adjusted_weight = adjusted_units['amount']
                    instance.adjusted_weight_unit = adjusted_units['unit']
                if instance.total_weight:
                    instance.adjusted_per_weight = instance.pack_cost
                    instance.extended_cost = instance.adjusted_per_weight * instance.total_weight
                    logger.debug(f"{instance.extended_cost!r} = {instance.pack_cost!r} * {instance.total_weight}")
                else:
                    instance.adjusted_pack_cost = instance.pack_cost
                    instance.extended_cost = instance.adjusted_pack_cost * instance.delivered_quantity
                    logger.debug(f"{instance.extended_cost!r} = {instance.pack_cost!r} * {instance.delivered_quantity}")
        form.save()
        return super().form_valid(form)
