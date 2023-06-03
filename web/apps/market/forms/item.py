from django import forms

from scrap.forms import fields as sc_fields
from market import models as mkt_models, utils


class ItemForm(forms.ModelForm):
    PACK_QUANTITIES = (
        (1, "Single"),
        (3, "3pk"),
        (4, "4pk"),
        (6, "6pk"),
        (8, "8pk"),
        (10, "10pk"),
        (12, "Dozen"),
    )
    name = forms.CharField()
    category = forms.ChoiceField(choices=utils.ITEM_CATEGORIES)
    item_pack_quantities = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, choices=PACK_QUANTITIES, required=False)
    tags = forms.ModelMultipleChoiceField(
        mkt_models.Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    material_cost_per_item = sc_fields.MoneyField(required=True)

    class Meta:
        model = mkt_models.Item
        fields = ['name', 'category', 'tags', 'material_cost_per_item']
