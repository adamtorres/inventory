import functools
import logging
import traceback

from django import forms
from django.contrib.postgres import forms as pg_forms
from django.core import exceptions
from django.forms import models

from scrap.forms import widgets as sc_widgets
from inventory import models as inv_models


logger = logging.getLogger(__name__)


class SourceItemCreateLineItemForm(forms.Form):
    individual_weights = pg_forms.SimpleArrayField(
        forms.DecimalField(max_digits=8, decimal_places=4),  # inv_models.SourceItem.individual_weights
        required=False,
    )

    class Meta:
        pass


class SourceItemCreateLineItemModelForm(forms.ModelForm):
    source_category = forms.CharField(widget=sc_widgets.AutocompleteWidget, required=False)
    item_code = forms.CharField(required=False)
    extra_code = forms.CharField(required=False)
    cryptic_name = forms.CharField(required=False)
    individual_weights = pg_forms.SimpleArrayField(forms.DecimalField(max_digits=8, decimal_places=4), required=False)

    class Meta:
        model = inv_models.SourceItem
        fields = '__all__'
        exclude = [
            "use_type", "remaining_quantity", "remaining_pack_quantity", "remaining_unit_quantity",
            "remaining_count_quantity", "discrepancy"
        ]

    def log(self, msg):
        function = "<unknown>"
        for line in traceback.extract_stack():
            if '/lib/' in line[0]:
                continue
            function = line[2]
            break
        # Odd.  The __name__ is returning SourceItemForm instead of SourceItemCreateLineItemModelForm
        # Tried @classmethod with cls.__name__ and got same thing.
        logger.debug(f"{self.__class__.__name__}.{function}|{msg}")

    def get_autocomplete_fields(self):
        ac_fields = [
            field for field in self.fields if isinstance(self.fields[field].widget, sc_widgets.AutocompleteWidget)]
        return ac_fields

    def get_formset_field_name(self, field_name, added_prefix=""):
        key = f"{added_prefix}{self.prefix}-{field_name}"
        return key

    def get_formset_field_name_and_value(self, field_name, as_cleaned=False, added_prefix=""):
        key = self.get_formset_field_name(field_name, added_prefix)
        if as_cleaned:
            value = self.cleaned_data.get(key)
            self.log(f"{key} = {value!r}")
            return key, value
        value = self.data.get(key)
        self.log(f"{key} = {value!r}")
        return key, value

    def autocomplete_field_clean(self, field_name):
        """ This is for when the user did not select from the dropdown and typed something. """
        key, form_value = self.get_formset_field_name_and_value(field_name)
        if field_name not in self.get_autocomplete_fields():
            # Field is not using AutocompleteWidget.  Nothing to do.
            return form_value
        visible_key, visible_value = self.get_formset_field_name_and_value(field_name + "-text", added_prefix="id_")
        self.log(f"Form:{key}({form_value!r}), Visible:{visible_key}({visible_value!r})")
        if visible_value and not form_value:
            # User typed instead of selecting from dropdown
            form_value = visible_value
        elif visible_value and (visible_value != form_value):
            # User typed something else.
            # TODO: What if the user typed something, then selected something from the dropdown?
            form_value = visible_value
        return form_value

    def clean_source_category(self):
        return self.autocomplete_field_clean('source_category')

    # def clean_item_code(self):
    #     return self.autocomplete_field_clean('item_code')
    #
    # def clean_extra_code(self):
    #     return self.autocomplete_field_clean('extra_code')
    #
    # def clean_cryptic_name(self):
    #     return self.autocomplete_field_clean('cryptic_name')


class MyBaseModelFormSet(models.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Unsure why but on a GET request, BaseModelFormSet does an unfiltered select.
        self.queryset = inv_models.SourceItem.objects.none()


SourceItemCreateLineItemModelFormSet = models.modelformset_factory(
    inv_models.SourceItem, SourceItemCreateLineItemModelForm, extra=0, can_delete=False, formset=MyBaseModelFormSet)
