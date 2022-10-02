from django.views import generic

from inventory import forms as inv_forms, models as inv_models


class SourceItemCreateView(generic.TemplateView):
    template_name = "inventory/sourceitem_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = inv_models.Source.objects.active_sources()
        context['categories'] = inv_models.SourceItem.objects.source_categories()
        print(f"SourceItemCreateView.get_context_data: self.request.method = {self.request.method}")
        if self.request.method == 'POST':
            print(f"POST: {self.request.POST}")
            order_form_data = None
            if self.request.POST.get("lineitemform-TOTAL_FORMS"):
                order_form_data = {
                    'delivered_date': self.request.POST.get("lineitemform-0-delivered_date"),
                    'source': self.request.POST.get("lineitemform-0-source"),
                    'customer_number': self.request.POST.get("lineitemform-0-customer_number"),
                    'order_number': self.request.POST.get("lineitemform-0-order_number"),
                    'po_text': self.request.POST.get("lineitemform-0-po_text"),
                }
            context['order_form'] = inv_forms.SourceItemCreateOrderForm(data=order_form_data)
            context['line_item_formset'] = inv_forms.SourceItemCreateLineItemModelFormSet(self.request.POST)
        if self.request.method == 'GET':
            context['order_form'] = inv_forms.SourceItemCreateOrderForm()
            context['line_item_formset'] = inv_forms.SourceItemCreateLineItemModelFormSet()
        return context

    # def get_success_url(self):
    #     return urls.reverse('usage_report', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

