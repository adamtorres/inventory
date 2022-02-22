from django import http, urls
from django.db import transaction
from django.views.generic import CreateView
from incoming import models as inc_models, forms as inc_forms


class IncomingGroupCreateView(CreateView):
    model = inc_models.IncomingItemGroup
    # form_class = inc_forms.IncomingGroupForm
    fields = ['source', 'descriptor', 'comment', 'action_date']

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['item_formset']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['item_formset'] = inc_forms.IncomingItemFormSet(self.request.POST)
        else:
            data['item_formset'] = inc_forms.IncomingItemFormSet()
        return data

    def get_success_url(self):
        return urls.reverse("incoming_group", kwargs={'pk': self.object.pk})
