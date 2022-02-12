from django import forms

from .. import widgets


class DollarField(forms.Field):
    widget = widgets.Dollar()
    disabled = True
