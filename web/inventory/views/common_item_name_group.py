import requests

from django import urls
from django.views import generic

from inventory import models as inv_models
from scrap import views as sc_views


class CommonItemNameGroupListView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/commonitemnamegroup_list.html"
    on_page_title = "Common Item Names"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['sources'] = inv_models.Source.objects.all().order_by('name')
        # context['categories'] = inv_models.Category.objects.all().order_by('name')
        # context['departments'] = inv_models.Department.objects.all().order_by('name')
        context['object_list'] = self.get_object_list()
        return context

    def get_object_list(self):
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_common_item_name_groups_list"))
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return []
        return resp.json()


class CommonItemNameGroupCreateView(sc_views.OnPageTitleMixin, generic.CreateView):
    model = inv_models.CommonItemNameGroup
    fields = []
    on_page_title = "Create Common Item Name"


class CommonItemNameGroupDetailView(sc_views.OnPageTitleMixin, generic.DetailView):
    model = inv_models.CommonItemNameGroup
    on_page_title = "Create Common Item Name"

# TODO: Need to work out how to add/change/delete names from group on a form.
