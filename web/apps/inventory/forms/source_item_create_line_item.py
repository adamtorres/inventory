import functools
from django import forms
from django.contrib.postgres import forms as pg_forms
from django.forms import formset_factory

from inventory import models as inv_models


class SourceItemCreateLineItemForm(forms.Form):
    individual_weights = pg_forms.SimpleArrayField(
        forms.DecimalField(max_digits=8, decimal_places=4),  # inv_models.SourceItem.individual_weights
        required=False,
    )

    class Meta:
        pass


class SourceItemCreateLineItemModelForm(forms.ModelForm):
    class Meta:
        model = inv_models.SourceItem
        fields = '__all__'
        widgets = {
            'source_category': forms.TextInput(attrs={'placeholder': 'category from source'}),
            'item_code': forms.TextInput(attrs={'placeholder': 'item code'}),
            'extra_code': forms.TextInput(attrs={'placeholder': 'extra code'}),
            'cryptic_name': forms.TextInput(attrs={'placeholder': 'name as appears on invoice/receipt'}),
            'verbose_name': forms.TextInput(attrs={'placeholder': 'cleaned up cryptic name'}),
            'common_name': forms.TextInput(attrs={'placeholder': 'a more human-readable name'}),
            'extra_notes': forms.TextInput(attrs={'placeholder': 'extra notes'}),
            'scanned_filename': forms.TextInput(attrs={'placeholder': 'scanned filename'}),
        }


_SourceItemCreateLineItemModelFormSet = formset_factory(SourceItemCreateLineItemModelForm, extra=0, can_delete=False)
SourceItemCreateLineItemModelFormSet = functools.partial(_SourceItemCreateLineItemModelFormSet, prefix='lineitemform')
