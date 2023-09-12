import datetime
import json
import logging
import zoneinfo

from django.core import exceptions
from django.db import models
from django.utils import text
from rest_framework import response, views

from .. import models as inv_models, serializers as inv_serializers

logger = logging.getLogger(__name__)


class APIChartDataView(views.APIView):
    serializer = inv_serializers.SourceItemGraphDataSerializer

    def get(self, request, *args, format=None, **kwargs):
        # TODO: Consider custom renderer - https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers
        try:
            search_criteria = inv_models.SearchCriteria.objects.get(url_slug__iexact=kwargs.get("report_name"))
            qs = search_criteria.get_search_queryset()
        except (inv_models.SearchCriteria.DoesNotExist, exceptions.ObjectDoesNotExist):
            qs = self.get_custom_quesyset(kwargs.get("report_name"))
        # qs = qs.filter(delivered_date__gte=datetime.datetime(2023, 1, 1, 0, 0, 0, 0, zoneinfo.ZoneInfo("US/Mountain")))
        data = inv_models.SourceItem.objects.price_history(initial_qs=qs)
        return response.Response(data)

    def get_custom_quesyset(self, report_name):
        if report_name.startswith("issues_"):
            report_name = report_name[7:]
            qs = inv_models.SearchCriteria.objects.get(url_slug__iexact=report_name).get_search_queryset()
        match report_name:
            # TODO: Bandaid - SearchCriteria needs to be able to handle excludes which means the main search page does.
            case "8oz-chocolate-milk":
                qs = qs.exclude(cryptic_name__icontains="m&m")
            case "8oz-white-milk":
                qs = qs.exclude(models.Q(cryptic_name__icontains="choc")|models.Q(cryptic_name__icontains="whole"))
            case "all-purpose-flour":
                qs = qs.exclude(cryptic_name__icontains="bobsred")
            case "butter":
                qs = qs.exclude(cryptic_name__icontains="margarine")
            case "10-pear":
                qs = qs.exclude(models.Q(cryptic_name__icontains="peach")|models.Q(cryptic_name__icontains="cocktail"))
            case "ground-beef":
                qs = qs.exclude(cryptic_name__icontains="beef ground pty")
            case "burger-patties":
                qs = qs.exclude(cryptic_name__icontains="beef ground pty")
                # npp nat beef ground pty nat 3\1 frz  --  6/1/22 and 6/15/22  --  did not get delivered.
                # Need to add an OR to the existing filter somehow.
            case _:
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('dz',)), ('name', ('egg',))])
        return qs
