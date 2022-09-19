from django import forms

from market import models as mkt_models


class IncomingGroupForm(forms.ModelForm):

    class Meta:
        model = mkt_models.Order
        fields = ['date_ordered', 'who', ]
