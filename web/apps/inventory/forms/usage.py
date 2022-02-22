from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

from inventory import models as inv_models


class UsageReportForm(forms.ModelForm):

    class Meta:
        model = inv_models.Usage
        fields = ['who', 'action_date']


class UsageReportItemForm(forms.ModelForm):

    class Meta:
        model = inv_models.UsageItem
        fields = ['item', 'unit_size', 'quantity', 'line_item_position']


UsageReportItemFormSet = inlineformset_factory(
    inv_models.Usage, inv_models.UsageItem, UsageReportItemForm,
    fields=['item', 'unit_size', 'quantity', 'line_item_position'], extra=0, can_delete=True
)
