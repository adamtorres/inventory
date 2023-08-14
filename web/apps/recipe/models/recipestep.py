# RecipeStep - Single step in the recipe?  Just a bit of text and sort order?
from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class RecipeStep(sc_models.DatedModel):
    recipe = models.ForeignKey(
        "recipe.Recipe", on_delete=models.CASCADE, related_name="steps", related_query_name="steps")
    step_number = models.IntegerField(default=1)
    optional = models.BooleanField(default=False, null=False, help_text="Can this step be skipped?")
    text = sc_fields.CharField(max_length=2048)

    class Meta:
        ordering = ['recipe', 'step_number']

    def __str__(self):
        return f"{self.step_number}: {sc_utils.cutoff(self.text)}"
