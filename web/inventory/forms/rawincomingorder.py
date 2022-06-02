import logging

from django import forms


logger = logging.getLogger(__name__)


class RawIncomingOrderForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)

    field_order = ['your_name']

    def save(self):
        logger.debug("RawIncomingOrderForm.save: Saving form...")
        logger.debug(f"RawIncomingOrderForm.save: cleaned_data = {self.cleaned_data}")
        return "new/updated object"


class RawIncomingItemForm(forms.Form):
    what = forms.CharField(label='Item Name', max_length=100)

    field_order = ['what']

    def save(self):
        logger.debug("RawIncomingItemForm.save: Saving form...")
        logger.debug(f"RawIncomingItemForm.save: cleaned_data = {self.cleaned_data}")
        return "new/updated object"


RawIncomingItemFormset = forms.formset_factory(RawIncomingItemForm, extra=1)
