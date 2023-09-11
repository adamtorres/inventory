import logging

from django.utils import text
from django.views import generic

from inventory import models as inv_models


logger = logging.getLogger(__name__)


class SourceItemSaveSearchView(generic.TemplateView):
    template_name = "inventory/sourceitem_save_search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["POST"] = self.request.POST
        context["GET"] = self.request.GET
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        search_criteria_to_save = {}
        for k in request.POST.keys():
            if k.startswith("save-") and request.POST[k]:
                search_criteria_to_save[k[5:]] = request.POST[k]
        if search_criteria_to_save:
            obj = inv_models.SearchCriteria.objects.create(
                name=request.POST["search-criteria-name"], description=request.POST["search-criteria-description"],
                criteria=search_criteria_to_save, category=request.POST["search-criteria-category"],
                # url_slug=text.slugify(request.POST["search-criteria-name"])  # Need to exclude "(Issues) "
            )
            obj.refresh_url_slug()
            obj.save()
            context["search_criteria"] = obj
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
        context['saved_searches'] = inv_models.SearchCriteria.objects.all()
        return context
