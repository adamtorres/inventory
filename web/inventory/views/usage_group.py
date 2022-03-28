import requests

from django import urls
from django.views import generic

from scrap import views as sc_views
from .. import models as inv_models, serializers as inv_serializers


class UsageGroupDetailView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/usagegroup_detail.html"
    on_page_title = "Usage"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        api_url = self.request.build_absolute_uri(
            urls.reverse("inventory:api_usage_group_detail", kwargs={'pk': kwargs['pk']}))
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        context['usagegroup'] = api_return_data
        return context


class UsageGroupListView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/usagegroup_list.html"
    on_page_title = "Usages"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = []
        api_get_data = {
            'format': 'json',
            'paging': 'off',
        }
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_usage_group_list"))
        resp = requests.get(api_url, params=api_get_data)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        if api_get_data['paging'] == 'off':
            # Unpaged results are not in an outer dict
            context['object_list'] = api_return_data
        else:
            context['object_list'] = api_return_data['results']
        return context
