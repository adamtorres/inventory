# RecipeComment - Any comments on how well people accepted it, ingredients to avoid, etc.
from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class RecipeComment(sc_models.DatedModel):
    recipe = models.ForeignKey(
        "recipe.Recipe", on_delete=models.CASCADE, related_name="comments", related_query_name="comments")
    comment = sc_fields.CharField(max_length=2048)
    pinned = models.BooleanField(default=False, help_text="Pinned comments will appear at the top of the list.")

    class Meta:
        ordering = ["recipe", "-pinned", "-created"]

    def __str__(self):
        return f"{self.modified}: {sc_utils.cutoff(self.comment)}"
