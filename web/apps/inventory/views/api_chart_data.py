import json
import logging

from django.db import models
from rest_framework import response, views

from .. import models as inv_models, serializers as inv_serializers

logger = logging.getLogger(__name__)


class APIChartDataView(views.APIView):
    serializer = inv_serializers.SourceItemGraphDataSerializer

    def get(self, request, *args, format=None, **kwargs):
        # TODO: Consider custom renderer - https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers

        # logger.debug(f"APIChartDataView.get: args={args}")
        # logger.debug(f"APIChartDataView.get: kwargs={kwargs}")
        # logger.debug(f"APIChartDataView.get: request.data={request.data}")
        # logger.debug(f"APIChartDataView.get: request.parser_context={request.parser_context}")
        # logger.debug(f"APIChartDataView.get: request.query_params={request.query_params}")

        match kwargs.get("report_name"):
            case "eggs":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('dz',)), ('name', ('egg', ))])
            case "beets":
                # TODO: convert these to use the saved searches?
                qs = inv_models.SourceItem.objects.wide_filter([('item_code', ('4109518',)), ('name', ('beet', )), ('source', ('sysco', 'us foods'))])
            case "2milk":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('8oz',)), ('name', ('milk', 'white', ))])
            case "chocmilk":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('8oz',)), ('name', ('milk', 'choc')), ('source', ('sysco', 'rsm', 'us foods'))])
            case "stringcheese":
                qs = inv_models.SourceItem.objects.wide_filter([('name', ('string', 'cheese'))])
            case "apflour":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('50lb',)), ('name', ('all', 'flour'))])
            case "butter":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('1lb',)), ('name', ('butter', ))])
                qs = qs.exclude(cryptic_name__icontains="margarine")
            case "margarine":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('1lb',)), ('name', ('margarine', ))])
            case "corn":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('#10',)), ('name', ('corn', ))])
            case "greenbeans":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('#10',)), ('name', ('green', 'bean'))])
            case _:
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('dz',)), ('name', ('egg',))])
        data = inv_models.SourceItem.objects.price_history(initial_qs=qs)
        return response.Response(data)
