"""
List distinct cryptic names and their combinations of item_codes, extra_codes, verbose and common names.
Include distinct pack/unit quantities and sizes.
"""
from django.contrib.postgres import fields as pg_fields, aggregates as pg_agg
from django.db import models
from django.db.models import expressions, functions

from .. import models as inv_models


class SourceItemNamesAndQuantities(object):
    key_fields = ['cryptic_name', 'verbose_name', 'common_name', 'item_code', 'extra_code']
    additional_agg_fields = ['delivered_quantity', 'pack_quantity']

    @staticmethod
    def get_queryset(grouping_fields: list, agg_fields: list, no_blanks=True):
        agg_fields_args = {
            agg_field: pg_agg.ArrayAgg(agg_field, distinct=True, ordering=[agg_field])
            for agg_field in agg_fields
        }
        qs = inv_models.SourceItem.objects.values(*grouping_fields)
        if no_blanks:
            exclude_filter = models.Q()
            for grouping_field in grouping_fields:
                exclude_filter |= models.Q(**{f"{grouping_field}__isnull": True})
                exclude_filter |= models.Q(**{f"{grouping_field}__exact": ""})
            qs = qs.exclude(exclude_filter)
        qs = qs.annotate(**agg_fields_args).order_by(*grouping_fields)
        return qs

    @classmethod
    def get_groupings(cls):
        all_fields = cls.key_fields + cls.additional_agg_fields
        for group_field in cls.key_fields:
            agg_fields = all_fields.copy()
            agg_fields.remove(group_field)
            print("=" * 80)
            print(f"Grouped by {group_field!r}")
            qs = cls.get_queryset([group_field], agg_fields)
            for line in qs:
                print(line)
            print()
