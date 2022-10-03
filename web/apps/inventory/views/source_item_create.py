from django import urls
from django.views import generic

from inventory import forms as inv_forms, models as inv_models


class SourceItemCreateView(generic.FormView):
    template_name = "inventory/sourceitem_create.html"
    form_class = inv_forms.SourceItemCreateLineItemModelFormSet
    prefix = "lineitemform"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["line_item_formset"] = context["form"]
        # context['sources'] = inv_models.Source.objects.active_sources()
        # context['categories'] = inv_models.SourceItem.objects.source_categories()
        if self.request.method == 'POST':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm(self.request.POST)
        if self.request.method == 'GET':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm()
        return context

    def get_success_url(self):
        return urls.reverse('inventory:sourceitem_search')

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
