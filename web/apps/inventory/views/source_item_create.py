from django.views import generic

from inventory import forms as inv_forms, models as inv_models


class SourceItemCreateView(generic.TemplateView):
    template_name = "inventory/sourceitem_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sources'] = inv_models.Source.objects.active_sources()
        context['categories'] = inv_models.SourceItem.objects.source_categories()
        context['order_form'] = inv_forms.SourceItemCreateOrderForm()
        context['line_item_formset'] = inv_forms.SourceItemCreateLineItemModelFormSet()
        return context
