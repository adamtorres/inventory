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
        qs_values = inc_models.IncomingItemGroup.objects.list_groups()[:5].values()
        for iig in qs_values:
            iig['selected'] = False
        return qs_values

    def get_success_url(self):
        return urls.reverse('incoming_groups')

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs

    def form_valid(self, form):
        iig_to_convert = []
        for item in form.cleaned_data:
            if item.get('selected'):
                iig_to_convert.append(item['id'])
        if iig_to_convert:
            print(f"Converting {len(iig_to_convert)} IIGs. {iig_to_convert}")
            # TODO: call the conversion function for each IIG.
        return super().form_valid(form)
