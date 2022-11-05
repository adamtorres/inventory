from django.views import generic

from scrap import utils

from inventory import models as inv_models


class SourceItemOrdersView(generic.TemplateView):
    template_name = "inventory/sourceitem_orders.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pass_along = ["source_id", "source", "order_number", "delivered_date"]
        for get_param in pass_along:
            if get_param in self.request.GET:
                context[f"pass_in_{get_param.replace('-', '_')}"] = self.request.GET[get_param]

        context['sources'] = inv_models.Source.objects.active_sources()
        return context
