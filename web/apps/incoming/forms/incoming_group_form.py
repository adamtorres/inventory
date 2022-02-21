from django import forms
from django.forms.models import inlineformset_factory, modelformset_factory

from incoming import models as inc_models
from scrap import forms as sc_forms, widgets as sc_widgets


class IncomingGroupForm(forms.ModelForm):

    class Meta:
        model = inc_models.IncomingItemGroup
        fields = ['source', 'descriptor', 'comment', 'action_date']


class IncomingItemForm(forms.ModelForm):
    template_name_table = 'incoming/forms/edit_item.html'
    # item = forms.CharField(widget=sc_widgets.AutocompleteWidget)
    item = forms.ModelChoiceField(inc_models.Item.objects.available_items(), widget=sc_widgets.AutocompleteWidget)
    ordered_quantity = forms.DecimalField()
    delivered_quantity = forms.DecimalField()
    total_weight = forms.DecimalField()
    pack_price = forms.DecimalField()
    pack_tax = forms.DecimalField()
    line_item_position = forms.IntegerField()
    comment = forms.CharField()

    class Meta:
        model = inc_models.IncomingItem
        fields = [
            'item', 'ordered_quantity', 'delivered_quantity', 'total_weight', 'pack_price', 'pack_tax',
            'line_item_position', 'comment']


IncomingItemFormSet = inlineformset_factory(
    inc_models.IncomingItemGroup, inc_models.IncomingItem, IncomingItemForm,
    fields=[
        'item', 'ordered_quantity', 'delivered_quantity', 'total_weight', 'pack_price', 'pack_tax',
        'line_item_position', 'comment'
    ], extra=0, can_delete=True
)

