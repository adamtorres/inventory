from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

from incoming import models as inc_models
from scrap import forms as sc_forms


class IncomingGroupForm(forms.ModelForm):

    class Meta:
        model = inc_models.IncomingItemGroup
        fields = ['source', 'descriptor', 'comment', 'action_date']


class IncomingItemForm(forms.ModelForm):
    class Meta:
        model = inc_models.IncomingItem
        fields = [
            'item', 'ordered_quantity', 'delivered_quantity', 'total_weight', 'pack_price', 'pack_tax',
            'line_item_position', 'comment']


IncomingItemFormSet = inlineformset_factory(
    inc_models.IncomingItemGroup, inc_models.IncomingItem,
    fields=[
        'item', 'ordered_quantity', 'delivered_quantity', 'total_weight', 'pack_price', 'pack_tax',
        'line_item_position', 'comment'
    ], extra=0, can_delete=True
)

