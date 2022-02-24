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
    item = forms.ModelChoiceField(inc_models.Item.objects.available_items(), widget=sc_widgets.AutocompleteWidget)
    ordered_quantity = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    delivered_quantity = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    total_weight = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    pack_price = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    pack_tax = forms.DecimalField(max_digits=10, decimal_places=4, required=False)
    line_item_position = forms.IntegerField()
    comment = forms.CharField(required=False)

    class Meta:
        model = inc_models.IncomingItem
        fields = [
            'item', 'ordered_quantity', 'delivered_quantity', 'total_weight', 'pack_price', 'pack_tax',
            'line_item_position', 'comment']

    def clean_total_weight(self):
        return self.cleaned_data['total_weight'] or 0.0

    def clean_pack_tax(self):
        return self.cleaned_data['pack_tax'] or 0.0

    def clean_comment(self):
        return self.cleaned_data['comment'] or ''

    def get_context(self):
        context = super().get_context()
        # TODO: I don't really like how the placeholder is being set for the AutocompleteWidget.
        # print("=" * 80)
        # print(f"IncomingItemForm.get_context: {context}")
        # print(f"item.html_name = {context['form']['item'].html_name}")
        value = context['form']['item'].value()
        # print(f"item.value() = {value}")
        if value:
            # print(f"item.form.is_bound = {context['form']['item'].form.is_bound}")
            # print(f"form.instance = {context['form'].instance}")
            # print(f"item.field.widget = {context['form']['item'].field.widget}")
            context['form']['item'].field.widget.attrs['placeholder'] = str(context['form'].instance)
        return context


IncomingItemFormSet = inlineformset_factory(
    inc_models.IncomingItemGroup, inc_models.IncomingItem, IncomingItemForm,
    fields=[
        'item', 'ordered_quantity', 'delivered_quantity', 'total_weight', 'pack_price', 'pack_tax',
        'line_item_position', 'comment'
    ], extra=0, can_delete=True
)
