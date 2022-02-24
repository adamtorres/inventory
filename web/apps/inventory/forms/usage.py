from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

from inventory import models as inv_models
from scrap import widgets as sc_widgets


class UsageReportForm(forms.ModelForm):

    class Meta:
        model = inv_models.Usage
        fields = ['who', 'action_date']


class UsageReportItemForm(forms.ModelForm):
    item = forms.ModelChoiceField(inv_models.Item.objects.available_items(), widget=sc_widgets.AutocompleteWidget)
    quantity = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    unit_size = forms.CharField(max_length=1024)
    line_item_position = forms.IntegerField()

    class Meta:
        model = inv_models.UsageItem
        fields = ['item', 'unit_size', 'quantity', 'line_item_position']


UsageReportItemFormSet = inlineformset_factory(
    inv_models.Usage, inv_models.UsageItem, UsageReportItemForm,
    fields=['item', 'unit_size', 'quantity', 'line_item_position'], extra=0, can_delete=True
)
