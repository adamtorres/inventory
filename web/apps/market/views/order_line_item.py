from django import urls
from django import http
from django.views import generic

from market import models as mkt_models, forms as mkt_forms


class OrderLineItemCreateView(generic.detail.SingleObjectMixin, generic.FormView):
    model = mkt_models.Order
    template_name = "market/order_line_item_create.html"
    object = None

    def form_valid(self, form):
        form.save()
        # TODO: messages.add_message(blah)
        return http.HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        return mkt_forms.OrderLineItemFormset(**self.get_form_kwargs(), instance=self.object)

    def get_success_url(self):
        return urls.reverse("market:order_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(OrderLineItemCreateView, self).post(request, *args, **kwargs)
