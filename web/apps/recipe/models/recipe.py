# Recipe - Common multipliers.
from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class Recipe(sc_models.DatedModel):
    # Foreign key to multiple Ingredients
    # Foreign key to multiple RecipeSteps
    name = sc_fields.CharField(blank=False)
    source = sc_fields.CharField(help_text="url if from a site.  Book/page, etc?")
    description = sc_fields.CharField(help_text="General description")
    reason_to_not_make = sc_fields.CharField(help_text="Argument to not make this.  More definitive for filtering")
    star_acceptance = models.IntegerField(null=True, help_text="How well did people like it?")
    star_effort = models.IntegerField(null=True, help_text="How much fun was it to make?")
    common_multipliers = pg_fields.ArrayField(models.IntegerField(), default=list, help_text="")

    def __str__(self):
        description = self.description if len(self.description) < 47 else f"{self.description[:47]}..."
        return f"{self.name}, {description}"
