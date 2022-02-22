from django import forms
from django.forms import formset_factory

from scrap import forms as sc_forms


class IncomingGroupListGenericForm(forms.Form):
    template_name_table = "incoming/forms/incomingitemgroup_list_table.html"

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


def as_my_table(self):
    """Render as <tr> elements excluding the surrounding <table> tag."""
    # Copied
    return self.render(self.template_name_my_table)


IncomingGroupListGenericFormSet = formset_factory(IncomingGroupListGenericForm, extra=0, can_delete=False)
setattr(IncomingGroupListGenericFormSet, 'template_name_my_table', "incoming/forms/my_table.html")
setattr(IncomingGroupListGenericFormSet, 'as_my_table', as_my_table)
