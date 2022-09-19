from django import urls
from django.contrib import messages
from django.views import generic

from market import models as mkt_models, forms as mkt_forms


class ItemPackQuantitiesMixin:
    form_class = mkt_forms.ItemForm

    def form_valid(self, form):
        ipq = [int(i) for i in form.cleaned_data.get("item_pack_quantities")]
        # Need the object saved in order to create the item_packs.
        ret = super().form_valid(form)
        self.object.refresh_from_db()
        existing = set(self.object.item_packs.all().values_list('quantity', flat=True))
        remove_quantities = existing.difference(ipq)
        new_quantities = set(ipq).difference(existing)
        if remove_quantities:
            self.object.item_packs.filter(quantity__in=remove_quantities).delete()
            remove_quantities_str = ", ".join(map(str, sorted(list(remove_quantities))))
            messages.success(self.request, f"Removed packs {remove_quantities_str}")
        if new_quantities:
            for new_qty in new_quantities:
                self.object.item_packs.create(
                    quantity=new_qty, material_cost_per_pack=new_qty * self.object.material_cost_per_item)
            new_quantities_str = ", ".join(map(str, sorted(list(new_quantities))))
            messages.success(self.request, f"Added packs {new_quantities_str}")
        return ret

    def get_initial(self):
        initial = super().get_initial()
        if hasattr(self, 'object') and getattr(self, 'object'):
            ipq = [str(i) for i in self.object.item_packs.all().values_list('quantity', flat=True)]
            initial['item_pack_quantities'] = ipq
        return initial


class ItemCreateView(ItemPackQuantitiesMixin, generic.CreateView):
    model = mkt_models.Item

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


class ItemUpdateView(ItemPackQuantitiesMixin, generic.UpdateView):
    model = mkt_models.Item

    def form_valid(self, form):
        messages.success(self.request, f"Updated {self.object}.")
        return super().form_valid(form)

    def get_success_url(self):
        return urls.reverse('market:item_detail', args=(self.object.id,))
