# Item - Ketchup, salt, chicken thigh - not tied to a recipe.  Just a level of separation between items needed for
# recipes and items we have in inventory.  As in, when adding a new recipe that uses an item we've never ordered, an
# Item object acts as the in-between.  When we do end up ordering something that matches, the Item can be updated.

from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class Item(sc_models.DatedModel):
    # TODO: How to link this to multiple SourceItems?  This could be "All Purpose Flour" but we have purchased a could
    #  different brands of APF and from different sources.

    name = sc_fields.CharField(blank=False)
    likely_source = sc_fields.CharField(help_text="Best guess where this would be purchased")
    description = sc_fields.CharField(help_text="General description")
    likely_container = sc_fields.CharField(help_text="To help with finding infrequently used items")

    class Meta:
        ordering = ['name', 'likely_source']

    def __str__(self):
        return self.name
