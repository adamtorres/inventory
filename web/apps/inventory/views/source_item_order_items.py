import logging

from django.views import generic

from scrap import utils

from inventory import models as inv_models


logger = logging.getLogger(__name__)


class SourceItemOrderItemsView(generic.TemplateView):
    template_name = "inventory/sourceitem_order_items.html"

    def get_context_data(self, **kwargs):
        logger.debug(f"SourceItemOrderItemsView.get_context_data: kwargs = {kwargs}")
        context = super().get_context_data(**kwargs)

        source_id = None
        source_name = kwargs.get('source')
        if utils.is_valid_uuid(source_name):
            source_id = source_name
            source_name = None
        delivered_date = kwargs.get('delivered_date')
        order_number = kwargs.get('order_number')
        if order_number == "nope":
            order_number = ""
        context['order_items'] = inv_models.SourceItem.objects.order_items(
            source_id=source_id, source_name=source_name, delivered_date=delivered_date, order_number=order_number)
        context['order'] = inv_models.SourceItem.objects.order_list(
            source_id=source_id, source_name=source_name, delivered_date=delivered_date, order_number=order_number)
        return context
