# SearchCriteria should have the same fields as the search page or wide filter.
# Goal: avoid hard coding searches like inventory/views/api_chart_data.py to find specific items.
# Need:
#   * name the search so it can be referenced in other places (recipe.item)
#   * calculations like price change over specific time, avg, high/low
# Would be nice:
#   * include an exclude set of filters in case there are some items which slip through?
#   * if attempting to save as existing name, ask to replace.  Would replace old search on any recipe.items currently
#     using the old search.  A replace function on SearchCriteria model?  new.replace(old) would do all the work?
#     Or old.replace_with(new_search_criteria) before a new object is created?

# urls.reverse("inventory:sourceitem_search") uses javascript to send a search packet to:
# urls.reverse("inventory:api_sourceitem_widefilter") which uses django_scrap.views.WideFilterView to process.

# Workflows:
#  Create:
#   User uses urls.reverse("inventory:sourceitem_search") to refine their search until the resulting items only include
#   what they want.
#   Button on page submits the search packet to a 'save search' form asking for a name, description, etc.
#  Use from search page:
#   Search page shows a drop down of saved searches allowing user to select which:
#     clears any existing search values
#     populates the form fields
#     performs the search
#  Edit:
#   Some management page allowing for editing?  Or should it be that the user would load an existing search, tweak it,
#   then save it as a new search.  They'd have to remove the old search and tie any recipe.items to the new search.
#  Delete:
#   Definitely need a delete option.  Would just null the value on the recipe.item.  A page with a list of searches and
#   checkboxes for deletion.


import json
import logging

from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class SearchCriteria(sc_models.DatedModel):
    name = sc_fields.CharField(help_text="hopefully unique name of this search")
    description = sc_fields.CharField(help_text="")
    # Should the fields and values be stored in a single field?  Parallel arrays?  json object?
    criteria = models.JSONField(default=dict)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"
