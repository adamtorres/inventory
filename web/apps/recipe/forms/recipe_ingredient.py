from django import forms

from scrap import measures as sc_measures
from scrap.forms import fields as sc_fields
from recipe import models as rcp_models


class RecipeIngredientForm(forms.ModelForm):
    template_name_table = "recipe/forms/recipe_ingredient_form_table.html"
    item = forms.ModelChoiceField(queryset=rcp_models.Item.objects.all())
    ingredient_number = forms.IntegerField(widget=forms.HiddenInput, required=False)
    optional = forms.BooleanField(required=False)
    us_quantity = forms.DecimalField(required=False)
    us_unit = forms.ChoiceField(choices=sc_measures.us_choice_list)
    metric_quantity = forms.DecimalField(required=False)
    metric_unit = forms.ChoiceField(choices=sc_measures.metric_choice_list)
    pre_preparation = sc_fields.CharField()

    class Meta:
        model = rcp_models.RecipeIngredient
        fields = [
            'item', 'ingredient_number', 'optional', 'pre_preparation', 'us_quantity', 'us_unit', 'metric_quantity',
            'metric_unit']


RecipeIngredientFormset = forms.inlineformset_factory(
    rcp_models.Recipe, rcp_models.RecipeIngredient, RecipeIngredientForm, extra=0, can_delete=True, can_order=True,
    can_delete_extra=True, )
