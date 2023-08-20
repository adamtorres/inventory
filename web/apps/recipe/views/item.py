import logging

from django import http, urls
from django.views import generic

from recipe import models as rcp_models, forms as rcp_forms


logger = logging.getLogger(__name__)


class ItemCreateView(generic.CreateView):
    model = rcp_models.Item
    fields = ['name', 'likely_source', 'description', 'likely_container', 'saved_search']

    def get_success_url(self):
        return urls.reverse('recipe:item_detail', args=(self.object.id,))


class ItemDetailView(generic.DetailView):
    queryset = rcp_models.Item.objects.all()


class ItemListView(generic.ListView):
    queryset = rcp_models.Item.objects.all()


class ItemUpdateView(generic.UpdateView):
    model = rcp_models.Item
    fields = ['name', 'likely_source', 'description', 'likely_container', 'saved_search']

    def get_success_url(self):
        return urls.reverse('recipe:item_detail', args=(self.object.id,))
