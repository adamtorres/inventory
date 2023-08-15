# SearchCriteria should have the same fields as the search page or wide filter.
# Goal: avoid hard coding searches like inventory/views/api_chart_data.py to find specific items.
# Need:
#   * name the search so it can be referenced in other places (recipe.item)
#   * calculations like price change over specific time, avg, high/low
# Would be nice:
#   * include an exclude set of filters in case there are some items which slip through?

import json
import logging

from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class SearchCriteria(sc_models.DatedModel):
    name = sc_fields.CharField(help_text="unique name of this search")
