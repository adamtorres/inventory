from django import urls
from django.views import generic

from incoming import models as inc_models, forms as inc_forms


class IncomingGroupItemLookupView(generic.FormView):
    template_name = "incoming/incoming_group_item_lookup.html"
    form_class = inc_forms.IncomingGroupItemFilterForm

    # def form_valid(self, form):
    #     pass

    def get_success_url(self):
        return urls.reverse("incoming_group_item_lookup")
