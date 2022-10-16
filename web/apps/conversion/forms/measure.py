import logging

from django import forms

from conversion import models as con_models


logger = logging.getLogger(__name__)


class MeasureForm(forms.ModelForm):
    avg_converted_per_measuring = forms.HiddenInput()

    class Meta:
        model = con_models.Measure
        fields = ["item", "measure_date", "measuring_unit", "measuring_count", "converted_unit", "converted_amount"]

    def save(self, commit=True):
        self.instance.avg_converted_per_measuring = (
                self.cleaned_data['converted_amount'] / self.cleaned_data['measuring_count'])
        self.instance.cryptic_name = self.instance.item.cryptic_name
        self.instance.verbose_name = self.instance.item.verbose_name
        self.instance.common_name = self.instance.item.common_name
        return super().save(commit=commit)
