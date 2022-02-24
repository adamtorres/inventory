from django import forms
from django.forms import formset_factory

from incoming import models as inc_models


class IncomingGroupItemFilterForm(forms.Form):
    name = forms.CharField(required=False)
    unit_size = forms.CharField(required=False)
    source = forms.ModelChoiceField(inc_models.Source.objects.active_sources(), required=False)
    pack_quantity = forms.CharField(required=False)

    # TODO: should pack_quantity be Char or Integer?
