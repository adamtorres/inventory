from django import forms
from django.contrib.postgres import forms as pg_forms

from inventory import models as inv_models


class SourceItemCreateOrderForm(forms.Form):
    delivered_date = forms.DateField(widget=forms.DateInput(attrs={'placeholder': '1/1/1970'}))
    source = forms.ModelChoiceField(queryset=inv_models.Source.objects.active_sources())
    # widget=forms.TextInput(attrs={'placeholder': 'Sysco, RSM, etc'})
    customer_number = forms.CharField(
        required=False, widget=forms.TextInput(attrs={'placeholder': '[no customer number]'}))
    order_number = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '[no order number]'}))
    po_text = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': '[no PO text]'}))

    class Meta:
        pass
