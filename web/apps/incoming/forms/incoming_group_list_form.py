from django import forms
from django.forms import formset_factory


class IncomingGroupListForm(forms.Form):
    template_name_table = "forms/table.html"

    id = forms.UUIDField(widget=forms.HiddenInput)
    converted_datetime = forms.DateTimeField(widget=forms.HiddenInput)

    selected = forms.BooleanField()
    converted_state = forms.CharField(disabled=True)
    source_name = forms.CharField(max_length=1024, disabled=True)
    action_date = forms.DateField(disabled=True)
    total_cost = forms.DecimalField(disabled=True)
    total_items = forms.IntegerField(disabled=True)
    total_pack_quantity = forms.DecimalField(disabled=True)
    descriptor = forms.CharField(max_length=1024, disabled=True)

    field_order = [
        'selected', 'converted_state', 'source_name', 'action_date', 'total_cost', 'total_items',
        'total_pack_quantity', 'descriptor']

    def is_valid(self):
        # This form is not data input/edit.  It is only to provide a checkbox.
        return True


IncomingGroupListFormSet = formset_factory(IncomingGroupListForm, extra=0, can_delete=False)
