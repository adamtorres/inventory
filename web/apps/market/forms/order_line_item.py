import decimal
import logging

from django import forms

from scrap.forms import fields as sc_fields
from market import models as mkt_models


logger = logging.getLogger(__name__)


class OrderLineItemForm(forms.ModelForm):
    template_name_table = "market/forms/order_line_item_form_table.html"
    line_item_position = forms.IntegerField()
    item = sc_fields.ComplicatedModelChoiceField(
        mkt_models.Item.objects.all(),
    )
    quantity = forms.IntegerField(required=False)
    packs = forms.IntegerField(required=False, label="Qty of Packs")
    pack_quantity = forms.IntegerField(initial=12)
    sale_price_per_pack = sc_fields.MoneyField()
    material_cost_per_pack = sc_fields.MoneyField()

    class Meta:
        model = mkt_models.OrderLineItem
        fields = [
            'line_item_position', 'item',  'quantity', 'packs', 'pack_quantity', 'sale_price_per_pack',
            'material_cost_per_pack']

    def clean_material_cost_per_pack(self):
        return self.cleaned_data['material_cost_per_pack'] or 0.0

    def clean_packs(self):
        return self.cleaned_data['packs'] or 0

    def clean_quantity(self):
        return self.cleaned_data['quantity'] or 0

    def save(self, commit=True):
        self.cleaned_data['quantity'] = (
                self.cleaned_data['packs'] * self.cleaned_data['pack_quantity'] + self.cleaned_data['quantity'])
        self.cleaned_data['material_cost_per_pack'] = decimal.Decimal(
                self.cleaned_data['item'].material_cost_per_item * self.cleaned_data['pack_quantity'])
        self.instance.quantity = self.cleaned_data['quantity']
        return super().save(commit=commit)


OrderLineItemFormset = forms.inlineformset_factory(
    mkt_models.Order, mkt_models.OrderLineItem, OrderLineItemForm,
    extra=0, can_delete=True,
)
