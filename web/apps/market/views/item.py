from django import urls
from django.views import generic

from market import models as mkt_models


class ItemCreateView(generic.CreateView):
    model = mkt_models.Item
    fields = ['name', 'category', 'material_cost_per_item']

    def get_success_url(self):
        return urls.reverse('market:item_detail', args=(self.object.id,))


class ItemDetailView(generic.DetailView):
    queryset = mkt_models.Item.objects.all()


class ItemListView(generic.ListView):
    queryset = mkt_models.Item.objects.all()


