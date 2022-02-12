from django import forms

from .. import widgets


class PlainField(forms.Field):
    widget = widgets.PlainText
    disabled = True

