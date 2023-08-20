# RecipeIngredient - Links Recipe, Item, and quantity.  Needs function to do multiplication of quantity.
from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models, utils as sc_utils, measures
from scrap.models import fields as sc_fields


class RecipeIngredient(sc_models.DatedModel):
    recipe = models.ForeignKey(
        "recipe.Recipe", on_delete=models.CASCADE, related_name="ingredients", related_query_name="ingredients")
    item = models.ForeignKey(
        "recipe.Item", on_delete=models.CASCADE, related_name="ingredients", related_query_name="ingredients")
    ingredient_number = models.IntegerField(default=0)
    optional = models.BooleanField(default=False, null=False, help_text="Can this ingredient be skipped")
    pre_preparation = sc_fields.CharField(help_text="Preprep for this ingredient: chopped/melted/room temp/etc")
    us_quantity = sc_fields.DecimalField()
    us_unit = sc_fields.CharField()
    metric_quantity = sc_fields.DecimalField()
    metric_unit = sc_fields.CharField()

    class Meta:
        ordering = ["recipe", "ingredient_number"]

    def __str__(self):
        # TODO: Is it worth adding cached text from Recipe and Item so this doesn't do another db hit?
        #  This should be displayed normally as it just links the other models.
        return f"{self.recipe.name}: {self.item.name}: {self.pre_preparation}"
