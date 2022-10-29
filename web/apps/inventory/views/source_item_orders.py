from django.views import generic

from scrap import utils

from inventory import models as inv_models


class SourceItemOrdersView(generic.TemplateView):
    template_name = "inventory/sourceitem_orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = inv_models.Source.objects.active_sources()
        # source_id = None
        # source_name = self.request.GET.get('source')
        # if utils.is_valid_uuid(source_name):
        #     source_id = source_name
        #     source_name = None
        # delivered_date = self.request.GET.get('delivered_date')
        # order_number = self.request.GET.get('order_number')
        # context['orders'] = inv_models.SourceItem.objects.order_list(
        #     source_id=source_id, source_name=source_name, delivered_date=delivered_date, order_number=order_number)
        return context
