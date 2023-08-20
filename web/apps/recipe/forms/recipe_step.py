from django import forms

from scrap.forms import fields as sc_fields
from recipe import models as rcp_models


class RecipeStepForm(forms.ModelForm):
    template_name_table = "recipe/forms/recipe_step_form_table.html"
    text = sc_fields.CharField()
    optional = forms.BooleanField(required=False)
    step_number = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = rcp_models.RecipeStep
        fields = ['text', 'optional', 'step_number']


RecipeStepFormset = forms.inlineformset_factory(
    rcp_models.Recipe, rcp_models.RecipeStep, RecipeStepForm, extra=1, can_delete=True, can_order=True,
    can_delete_extra=True, )
