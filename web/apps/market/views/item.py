from django import urls
from django.contrib import messages
from django.views import generic

from market import models as mkt_models, forms as mkt_forms


class ItemCreateView(generic.CreateView):
    model = mkt_models.Item
    fields = ['name', 'category', 'tags', 'material_cost_per_item']

    def form_valid(self, form):
        ret = super().form_valid(form)
        messages.success(self.request, f"Created {self.object}.")
        return ret

    def get_success_url(self):
        return urls.reverse('market:item_detail', args=(self.object.id,))


class ItemDetailView(generic.DetailView):
    queryset = mkt_models.Item.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ItemDetailView, self).get_context_data(**kwargs)
        context['messages'] = messages.get_messages(self.request)
        return context


class ItemListView(generic.ListView):
    queryset = mkt_models.Item.objects.all()


class ItemUpdateView(generic.UpdateView):
    model = mkt_models.Item
    fields = ['name', 'category', 'tags', 'material_cost_per_item']

    def form_valid(self, form):
        messages.success(self.request, f"Updated {self.object}.")
        return super().form_valid(form)

    def get_success_url(self):
        return urls.reverse('market:item_detail', args=(self.object.id,))
