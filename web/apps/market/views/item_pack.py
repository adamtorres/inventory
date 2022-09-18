from django import urls
from django.views import generic

from market import models as mkt_models


class ItemPackCreateView(generic.CreateView):
    context_object_name = "item_pack"
    model = mkt_models.ItemPack
    fields = ['item', 'quantity']
    template_name = "market/item_pack_form.html"

    def get_success_url(self):
        return urls.reverse('market:item_pack_detail', args=(self.object.id,))


class ItemPackDetailView(generic.DetailView):
    context_object_name = "item_pack"
    queryset = mkt_models.ItemPack.objects.all()
    template_name = "market/item_pack_detail.html"


class ItemPackListView(generic.ListView):
    context_object_name = "item_pack_list"
    queryset = mkt_models.ItemPack.objects.all()
    template_name = "market/item_pack_list.html"


