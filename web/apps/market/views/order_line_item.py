from django import http, urls
from django.views import generic

from market import models as mkt_models, forms as mkt_forms


class OrderLineItemEditView(generic.detail.SingleObjectMixin, generic.FormView):
    model = mkt_models.Order
    template_name = "market/order_line_item_edit.html"
    object = None

    def form_valid(self, form):
        form.save()
        # TODO: messages.add_message(blah)
        self.object.calculate_totals()
        return http.HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO: Is this needed?  Or was this stubbed to add some logging?
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        # The base get_form does not pass the instance kwarg.
        return mkt_forms.OrderLineItemFormset(**self.get_form_kwargs(), instance=self.object)

    def get_success_url(self):
        return urls.reverse("market:order_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
