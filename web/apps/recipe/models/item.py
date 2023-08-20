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
    saved_search = models.ForeignKey(
        "inventory.SearchCriteria", on_delete=models.SET_NULL, related_name="recipe_items",
        related_query_name="recipe_items", null=True, default=None)

    class Meta:
        ordering = ['name', 'likely_source']

    def __str__(self):
        return self.name

    def get_current_cost_data(self):
        """
        Uses the saved search to find the most recent item and returns its cost.

        :return: dict with per_use_cost and pack_cost.
        """
        if not self.saved_search:
            return {
                "per_use_cost": 0.0,
                "pack_cost": 0.0,
            }
        last_result = self.saved_search.get_last_result()
        return {
            "per_use_cost": last_result.per_use_cost(),
            "pack_cost": last_result.calculated_pack_cost(),
        }
