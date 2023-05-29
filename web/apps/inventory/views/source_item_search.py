from django.views import generic

from inventory import models as inv_models


class SourceItemSearchView(generic.TemplateView):
    template_name = "inventory/sourceitem_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pass_along = [
            "item-id", "pick-first", "pick-id", "quantity", "unit-size", "item-code", "item-name", "comment",
            "order-number"]
        for get_param in pass_along:
            if get_param in self.request.GET:
                context[f"pass_in_{get_param.replace('-', '_')}"] = self.request.GET[get_param]

        context['sources'] = inv_models.Source.objects.active_sources()
        context['categories'] = inv_models.SourceItem.objects.source_categories()
        return context
