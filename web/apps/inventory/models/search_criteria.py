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

from django import urls
from django.db import models
import requests

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


logger = logging.getLogger(__name__)


class SearchCriteria(sc_models.DatedModel):
    name = sc_fields.CharField(help_text="hopefully unique name of this search")
    description = sc_fields.CharField(help_text="")
    # Should the fields and values be stored in a single field?  Parallel arrays?  json object?
    criteria = models.JSONField(default=dict)
    category = sc_fields.CharField(help_text="Self-defined category as some vendors seem to randomly assign them")

    form_field_ajax_var_xlate = {
        "filter-item-id": "item_id",
        "filter-source": "source",
        "filter-category": "category",
        "filter-quantity": "quantity",
        "filter-unit-size": "unit_size",
        "filter-item-name": "name",
        "filter-item-code": "item_code",
        "filter-comment": "comment",
        "filter-order-number": "order_number",
    }

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.category} / {self.name}"

    def form_field_to_ajax_var(self, form_field_name):
        return self.form_field_ajax_var_xlate.get(form_field_name)

    def get_search_queryset(self):
        from . import SourceItem
        vts = []
        for crit, value in self.criteria.items():
            ajax_var = self.form_field_to_ajax_var(crit[5:] if crit.startswith("save-") else crit)
            vts.append((ajax_var, value))
        qs = SourceItem.objects.wide_filter(vts)
        qs = qs.exclude(models.Q(delivered_quantity__lte=0) | models.Q(extended_cost__lte=0))
        qs = qs.order_by().order_by('delivered_date', 'source_id', 'order_number', 'line_item_number')
        return qs

    def search_so_bad_its_like_a_trainwreck(self):
        """
        Started this because I wanted to call the API and decided to use requests.  Then used the serializer to validate
        the response.  Then finally remembered there's a more direct way to use the wide filter using the model manager.
        :return:
        """
        DeprecationWarning("Don't use this mess.  Left here as a warning.")
        vts = {
            "wide_filter_fields[]": [],
            "empty": True,
        }
        for crit, value in self.criteria.items():
            logger.debug(f"SearchCriteria.search: crit={crit!r}, value={value!r}")
            ajax_var = self.form_field_to_ajax_var(crit[5:] if crit.startswith("save-") else crit)
            vts[ajax_var] = value
            vts["wide_filter_fields[]"].append(ajax_var)
            if value:
                vts["empty"] = False

        logger.debug(f"SearchCriteria.search: {vts}")
        resp = requests.get("http://localhost:8000" + urls.reverse("inventory:api_sourceitem_widefilter"), params=vts)
        logger.debug(f"SearchCriteria.search: status_code = {resp.status_code}")
        # logger.debug(f"SearchCriteria.search: text = {resp.json()}")
        if resp.status_code != 200:
            logger.error(f"Failed getting api result.  status code is {resp.status_code!r}")
            return None
        jd = resp.json()
        # For some reason, the serializer fails on individual weights having an empty list.
        for item in jd:
            if not len(item["individual_weights"]):
                item["individual_weights"].append(0)
        # Avoiding circular imports.  Might mean this function shouldn't be here.
        from inventory import serializers as inv_serializers
        ser = inv_serializers.SourceItemWideFilterSerializer(data=jd, many=True)
        if not ser.is_valid():
            logger.error(f"Failed deserialization: {ser.errors}")
            return False
        for item in ser.validated_data:
            logger.debug(
                f"Item: {item['delivered_date']} {item['order_number']} {item['line_item_number']} "
                f"{item['cryptic_name']} {item['item_code']} {item['pack_cost']}")

    def get_last_result(self):
        qs = self.get_search_queryset()
        return qs.last()


