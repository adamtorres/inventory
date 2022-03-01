from django import urls
from django.db import models
from django.views import generic

from incoming import models as inc_models
from inventory import models as inv_models


class DupeItemView(generic.TemplateView):
    template_name = "incoming/dupe_item.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # TODO: group by name and show dupes - highlight differences - show action_dates?
        # TODO: group by identifier and show dupes - highlight differences - show action_dates?
        dupes = inc_models.Item.objects.dupes_dict('name')
        if "" in dupes.keys():
            dupes["[empty string]"] = dupes[""]
            dupes.pop("")
        context["dupes_by_name"] = dupes
        context["dupes_by_name_count"] = len(context["dupes_by_name"])
        dupes = inc_models.Item.objects.dupes_dict('identifier')
        if "" in dupes.keys():
            dupes["[empty string]"] = dupes[""]
            dupes.pop("")
        context["dupes_by_identifier"] = dupes
        context["dupes_by_identifier_count"] = len(context["dupes_by_identifier"])
        return context


class MissingCommonItemView(generic.TemplateView):
    template_name = "incoming/missing_common_item.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = inc_models.Item.objects.select_related('source').order_by('source__name', 'name', 'identifier')
        context["missing_common_item"] = qs.exclude(common_item__isnull=False)
        return context
