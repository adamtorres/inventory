from django import forms

from scrap.forms import fields as sc_fields
from market import models as mkt_models, utils


class ItemForm(forms.ModelForm):
    name = forms.CharField()
    category = forms.ChoiceField(choices=utils.ITEM_CATEGORIES)
    tags = forms.ModelMultipleChoiceField(
        mkt_models.Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    material_cost_per_item = sc_fields.MoneyField(required=True)

    class Meta:
        model = mkt_models.Item
        fields = ['name', 'category', 'tags', 'material_cost_per_item']
