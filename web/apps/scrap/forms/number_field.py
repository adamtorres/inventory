from django import forms

from .. import widgets


class NumberField(forms.Field):
    widget = widgets.Number()
    disabled = True
