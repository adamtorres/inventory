from django import forms

from scrap.forms import fields as sc_fields
from recipe import models as rcp_models


class RecipeCommentForm(forms.ModelForm):
    template_name_table = "recipe/forms/recipe_comment_form_table.html"
    comment = sc_fields.CharField()
    pinned = forms.BooleanField(required=False)

    class Meta:
        model = rcp_models.RecipeComment
        fields = ['comment', 'pinned']


RecipeCommentFormset = forms.inlineformset_factory(
    rcp_models.Recipe, rcp_models.RecipeComment, RecipeCommentForm, extra=1, can_delete=True)
