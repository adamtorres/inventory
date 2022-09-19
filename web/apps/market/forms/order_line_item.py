from django import forms

from scrap.forms import fields as sc_fields
from market import models as mkt_models


class OrderLineItemForm(forms.ModelForm):
    template_name_table = "market/forms/order_line_item_form_table.html"
    line_item_position = forms.IntegerField()
    item_pack = forms.ModelChoiceField(mkt_models.ItemPack.objects.all())  # widget=sc_widgets.AutocompleteWidget
    quantity = forms.IntegerField()
    sale_price_per_pack = sc_fields.MoneyField()
    material_cost_per_pack = sc_fields.MoneyField()

    class Meta:
        model = mkt_models.OrderLineItem
        fields = ['line_item_position', 'item_pack',  'quantity',  'sale_price_per_pack', 'material_cost_per_pack']

    # def clean_material_cost_per_pack(self):
    #     return self.cleaned_data['material_cost_per_pack'] or 0.0
    #
    # def clean_sale_price_per_pack(self):
    #     return self.cleaned_data['sale_price_per_pack'] or 0.0

    def get_context(self):
        context = super().get_context()
        # TODO: I don't really like how the placeholder is being set for the AutocompleteWidget. (copied from v3-old)
        # value = context['form']['item'].value()
        # if value:
        #     context['form']['item'].field.widget.attrs['placeholder'] = str(context['form'].instance)
        return context


OrderLineItemFormset = forms.inlineformset_factory(
    mkt_models.Order, mkt_models.OrderLineItem, OrderLineItemForm,
    # fields=('line_item_position', 'item_pack',  'quantity',  'sale_price_per_pack', 'material_cost_per_pack',),
    extra=0, can_delete=True,
)
