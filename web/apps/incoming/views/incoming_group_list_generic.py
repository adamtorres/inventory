from django import urls
from django.db import models
from django.views.generic import ListView, FormView

from incoming import models as inc_models, forms as inc_forms


class IncomingGroupView(FormView):
    """
    Using the ListView to show the IIGs instead of manually making everthing.
    """
    model = inc_models.IncomingItemGroup
    template_name = "incoming/incomingitemgroup_list.html"
    form_class = inc_forms.IncomingGroupListGenericFormSet

    # def get_context_data(self, *args, object_list=None, **kwargs):
    #     context = super().get_context_data(object_list=object_list, **kwargs)
    #     return context

    def get_initial(self):
        qs_values = self.get_queryset().values()
        count = 0
        selectable = 0
        for iig in qs_values:
            count += 1
            if not iig['converted_datetime']:
                iig['selected'] = False
                selectable += 1
            if count == 1:
                print(iig)
        return qs_values

    def get_queryset(self):
        qs = self.model.objects.list_groups()
        qs = qs.prefetch_related('source', 'items')
        return qs.order_by('-action_date')

    def get_success_url(self):
        return urls.reverse("bob")

    def form_valid(self, form):
        iigs_to_convert = []
        for f in form.forms:
            if f.cleaned_data.get('selected', False):
                iigs_to_convert.append(f.cleaned_data.get('id'))
        if iigs_to_convert:
            print(f"Convert these: {iigs_to_convert}")
        return super().form_valid(form)
