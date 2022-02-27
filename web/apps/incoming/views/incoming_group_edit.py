from django import http
from django.db import transaction
from django.views.generic import UpdateView
from incoming import models as inc_models, forms as inc_forms


class IncomingGroupUpdateView(UpdateView):
    model = inc_models.IncomingItemGroup
    # form_class = inc_forms.IncomingGroupForm
    fields = ['source', 'descriptor', 'comment', 'action_date']

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('source', 'items', 'items__item', 'items__item__common_item')
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['on_page_title'] = "Edit Item Group"
        if self.request.POST:
            data['item_formset'] = inc_forms.IncomingItemFormSet(self.request.POST)
            print(f"POST: {data['item_formset'].__dict__}")
        else:
            data['item_formset'] = inc_forms.IncomingItemFormSet(instance=self.object)
            print(f"GET: {data['item_formset'].__dict__}")
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        items = context['item_formset']
        with transaction.atomic():
            self.object = form.save()
            if items.is_valid():
                items.instance = self.object
                items.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        if "cancel" in request.POST:
            self.object = self.get_object()
            url = self.get_success_url()
            return http.HttpResponseRedirect(url)
        return super().post(request, *args, **kwargs)
