from django import forms
from django.forms import formset_factory

from scrap import forms as sc_forms


class IncomingGroupListGenericForm(forms.Form):
    template_name_table = "incoming/forms/table.html"

    id = forms.CharField(widget=forms.HiddenInput)
    selected = forms.BooleanField()
    converted_state = sc_forms.PlainField()
    source_name = sc_forms.PlainField()
    action_date = sc_forms.PlainField()
    descriptor = sc_forms.PlainField()
    comment = sc_forms.PlainField()
    total_items = sc_forms.NumberField()
    total_packs = sc_forms.NumberField()
    total_price = sc_forms.DollarField()

    def is_valid(self):
        # This form is not data input/edit.  It is only to provide a checkbox.
        return True


IncomingGroupListGenericFormSet = formset_factory(IncomingGroupListGenericForm, extra=0, can_delete=False)
