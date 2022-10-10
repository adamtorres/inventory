from django import forms
from django.contrib.postgres import forms as pg_forms
from django.forms import models

import scrap.forms.widgets
from inventory import models as inv_models


class SourceItemCreateLineItemForm(forms.Form):
    individual_weights = pg_forms.SimpleArrayField(
        forms.DecimalField(max_digits=8, decimal_places=4),  # inv_models.SourceItem.individual_weights
        required=False,
    )

    class Meta:
        pass


class SourceItemCreateLineItemModelForm(forms.ModelForm):
    source_category = forms.CharField(widget=scrap.forms.widgets.AutocompleteWidget)
    item_code = forms.CharField(widget=scrap.forms.widgets.AutocompleteWidget)
    extra_code = forms.CharField(widget=scrap.forms.widgets.AutocompleteWidget)
    cryptic_name = forms.CharField(widget=scrap.forms.widgets.AutocompleteWidget)
    verbose_name = forms.CharField(widget=scrap.forms.widgets.AutocompleteWidget)
    common_name = forms.CharField(widget=scrap.forms.widgets.AutocompleteWidget)

    class Meta:
        model = inv_models.SourceItem
        fields = '__all__'
        exclude = [
            "use_type", "remaining_quantity", "remaining_pack_quantity", "remaining_unit_quantity",
            "remaining_count_quantity", "discrepancy"
        ]
        # widgets = {
        #     'source_category': forms.TextInput(attrs={'placeholder': ''}),
        #     'item_code': forms.TextInput(attrs={'placeholder': 'item code'}),
        #     'extra_code': forms.TextInput(attrs={'placeholder': 'extra code'}),
        #     'cryptic_name': forms.TextInput(attrs={'placeholder': 'name as appears on invoice/receipt'}),
        #     'verbose_name': forms.TextInput(attrs={'placeholder': 'cleaned up cryptic name'}),
        #     'common_name': forms.TextInput(attrs={'placeholder': 'a more human-readable name'}),
        #     'extra_notes': forms.TextInput(attrs={'placeholder': 'extra notes'}),
        #     'scanned_filename': forms.TextInput(attrs={'placeholder': 'scanned filename'}),
        # }


class MyBaseModelFormSet(models.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Unsure why but on a GET request, BaseModelFormSet does an unfiltered select.
        self.queryset = inv_models.SourceItem.objects.none()


SourceItemCreateLineItemModelFormSet = models.modelformset_factory(
    inv_models.SourceItem, SourceItemCreateLineItemModelForm, extra=0, can_delete=False, formset=MyBaseModelFormSet)
