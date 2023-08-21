from collections import defaultdict
import logging

from django.views import generic

from inventory import models as inv_models

logger = logging.getLogger(__name__)


class SearchCriteriaCurrentPricesView(generic.TemplateView):
    template_name = "inventory/searchcriteria_current_prices.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        items = [
            {"item": o.get_last_result(), "description": o.description, "category": o.category}
            for o in inv_models.SearchCriteria.objects.all().order_by('category', 'name')
        ]
        grouped_items = defaultdict(list)
        for item_x in items:
            item = item_x["item"]
            item_x.update({
                'source_name': item.source_name, 'common_name': item.common_name,
                'last_order_date': item.delivered_date, 'quantity': (item.pack_quantity * item.unit_quantity),
                'pack_cost': item.pack_cost, 'per_use_cost': item.per_use_cost(),
            })
            grouped_items[item_x['category']].append(item_x)
        context["grouped_items"] = dict(grouped_items)
        return context
