from django import forms
from django.forms import formset_factory


class IncomingGroupListForm(forms.Form):
    selected = forms.CheckboxInput()
    # incoming_group_id = forms.HiddenInput()
    action_date = forms.DateField(disabled=True)
    descriptor = forms.CharField(max_length=1024, disabled=True)

    def get_initial_for_field(self, field, field_name):
        print(f"Form.get_initial_for_field({field}, {field_name})")
        return super().get_initial_for_field(field, field_name)

    def get_context(self):
        print("Form.get_context")
        return super().get_context()


IncomingGroupListFormSet = formset_factory(IncomingGroupListForm, extra=0, can_delete=False)
