import logging

from django.views import generic

from inventory import models as inv_models

logger = logging.getLogger(__name__)


class SearchCriteriaCurrentPricesView(generic.TemplateView):
    template_name = "inventory/searchcriteria_current_prices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {"item": o.get_last_result(), "description": o.description} for o in inv_models.SearchCriteria.objects.all()
        ]
        report_data = []
        for item_x in items:
            item = item_x["item"]
            report_data.append({
                'source_name': item.source_name, 'common_name': item.common_name, 'description': item_x['description'],
                'last_order_date': item.delivered_date, 'quantity': (item.pack_quantity * item.unit_quantity),
                'pack_cost': item.pack_cost, 'per_use_cost': item.per_use_cost(), "item": item,
            })
        context["items"] = report_data
        return context
