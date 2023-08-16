from django.views import generic

from inventory import models as inv_models


class SourceItemSaveSearchView(generic.TemplateView):
    template_name = "inventory/sourceitem_save_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["POST"] = self.request.POST
        context["GET"] = self.request.GET
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)


class SourceItemSearchView(generic.TemplateView):
    template_name = "inventory/sourceitem_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pass_along = [
            "item-id", "pick-first", "pick-id", "quantity", "unit-size", "item-code", "item-name", "comment",
            "order-number", "source-id"]
        for get_param in pass_along:
            if get_param in self.request.GET:
                # TODO: Handle multiple values in the case of selecting multiple sources.
                context[f"pass_in_{get_param.replace('-', '_')}"] = self.request.GET[get_param]

        context['sources'] = inv_models.Source.objects.active_sources()
        context['categories'] = inv_models.SourceItem.objects.source_categories()
        return context
