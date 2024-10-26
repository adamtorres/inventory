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
        search_criteria = inv_models.SearchCriteria.objects.get(url_slug__iexact=kwargs.get("report_name"))
        qs = search_criteria.get_search_queryset()
        qs = qs.filter(delivered_date__gte=datetime.datetime(2022, 1, 1, 0, 0, 0, 0, zoneinfo.ZoneInfo("US/Mountain")))
        data = inv_models.SourceItem.objects.price_history(initial_qs=qs)
        return response.Response(data)
