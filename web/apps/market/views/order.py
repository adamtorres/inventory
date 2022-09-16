from django import urls
from django.views import generic

from market import models as mkt_models


class OrderCreateView(generic.CreateView):
    model = mkt_models.Order
    fields = [
        'item_pack',
        'quantity',
        'date_ordered',
        'who',
        'sale_price_per_pack',
        'sale_price',
        'material_cost_per_pack',
        'material_cost',
    ]

    def get_success_url(self):
        return urls.reverse('market:order_detail', args=(self.object.id,))


class OrderDetailView(generic.DetailView):
    queryset = mkt_models.Order.objects.all()


class OrderListView(generic.ListView):
    queryset = mkt_models.Order.objects.all()


