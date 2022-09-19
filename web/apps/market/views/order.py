from django import urls
from django import http
from django.views import generic

from market import models as mkt_models


class OrderCreateView(generic.CreateView):
    model = mkt_models.Order
    fields = [
        'date_ordered',
        'who',
        # 'sale_price',
        # 'material_cost',
    ]

    def get_success_url(self):
        return urls.reverse('market:order_detail', args=(self.object.id,))


class OrderDetailView(generic.DetailView):
    queryset = mkt_models.Order.objects.all()


class OrderListView(generic.ListView):
    include_completed = True

    def get(self, request, *args, **kwargs):
        self.include_completed = request.GET.get('completed', '').lower() == "true"
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['include_completed'] = self.include_completed
        return context

    def get_queryset(self):
        if self.include_completed:
            return mkt_models.Order.objects.all()
        else:
            return mkt_models.Order.objects.incomplete()


class OrderModifyByActionView(generic.View):
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        list_url = urls.reverse('market:order_list')
        try:
            obj = mkt_models.Order.objects.get(pk=pk)
        except mkt_models.Order.DoesNotExist:
            print(f"Order {pk!r} not found.")
            return http.HttpResponseRedirect(list_url)
        except mkt_models.Order.MultipleObjectsReturned:
            print(f"Order {pk!r} returned multiple records.")
            return http.HttpResponseRedirect(list_url)
        url = urls.reverse('market:order_detail', args=(obj.id,))

        modify_action = request.POST.get('modify-action')
        if modify_action == 'made' and obj.can_be_made():
            obj.set_order_made()
        if modify_action == 'picked-up' and obj.can_be_picked_up():
            obj.set_order_picked_up()
        return http.HttpResponseRedirect(url)

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
