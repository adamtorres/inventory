from django import urls
from django.views import generic

from incoming import models as inc_models, forms as inc_forms


class IncomingGroupListView(generic.FormView):
    template_name = "incoming/incoming_group_list.html"
    form_class = inc_forms.IncomingGroupListFormSet

    def get_initial(self):
        # TODO: Loading IncomingGroupListView page is slow.
        qs_values = inc_models.IncomingItemGroup.objects.list_groups().filter(converted_datetime__isnull=True).values()
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
            for iig in inc_models.IncomingItemGroup.objects.filter(id__in=iig_to_convert):
                iig.convert_to_change_from_iig()
        return super().form_valid(form)
