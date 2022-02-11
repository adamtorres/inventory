from django import urls
from django.db import models
from django.views import generic
from django.utils import timezone

from dateutil import relativedelta

from incoming import models as inc_models, forms as inc_forms
import scrap


class IncomingGroupListView(generic.FormView):
    template_name = "incoming/incoming_group_list.html"
    form_class = inc_forms.IncomingGroupListFormSet

    def get_initial(self):
        print("View.get_initial")
        data = inc_models.IncomingItemGroup.objects.list_groups_by_converted_state(scrap.first_of_month())
        # source_name, total_cost, total_items, total_pack_quantity, action_date
        # return Model.objects.filter(status='whatever').values()  # values() is required

        return super().get_initial()

    def get_success_url(self):
        return urls.reverse('incoming_groups')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        limit_to = scrap.first_of_month() - relativedelta.relativedelta(months=6)
        data = inc_models.IncomingItemGroup.objects.list_groups_by_converted_state()
        kwargs.update(data)
        return kwargs

    def form_valid(self, form):
        print(f"yay! {form.cleaned_data}")
        return super().form_valid(form)
