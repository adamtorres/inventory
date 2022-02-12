from django import forms
from django.forms import formset_factory


class IncomingGroupListGenericForm(forms.Form):
    selected = forms.BooleanField()

    def is_valid(self):
        # This form is not data input/edit.  It is only to provide a checkbox.
        return True


IncomingGroupListGenericFormSet = formset_factory(IncomingGroupListGenericForm, extra=0, can_delete=False)
