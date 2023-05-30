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
                qs = inv_models.SourceItem.objects.wide_filter([('item_code', ('4109518',)), ('name', ('beet', )), ('source', ('sysco',))])
            case "2milk":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('8oz',)), ('name', ('milk', 'white'))])
            case "chocmilk":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('8oz',)), ('name', ('milk', 'choc')), ('source', ('sysco', 'rsm'))])
            case "stringcheese":
                qs = inv_models.SourceItem.objects.wide_filter([('name', ('string', 'cheese'))])
            case "apflour":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('50lb',)), ('name', ('all', 'flour'))])
            case "butter":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('1lb',)), ('name', ('butter', ))])
            case "margarine":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('1lb',)), ('name', ('margarine', ))])
            case "corn":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('#10',)), ('name', ('corn', ))])
            case "greenbeans":
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('#10',)), ('name', ('green', 'bean'))])
            case _:
                qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('dz',)), ('name', ('egg',))])

        qs = qs.exclude(models.Q(delivered_quantity__lte=0) | models.Q(extended_cost__lte=0))
        qs = qs.order_by().order_by('delivered_date', 'source_id', 'order_number', 'line_item_number')
        data = {
            'item_names': set(),
            'item_name': [], 'delivered_date': [], 'per_use_cost': [], 'initial_quantity': [], 'pack_cost': [],
            # '': [],
            'source': [],
        }
        for si in qs:
            data['item_names'].add(f"{si.verbose_name or si.cryptic_name} {si.unit_size}")
            data['delivered_date'].append(si.delivered_date)
            data['per_use_cost'].append(si.per_use_cost())
            data['initial_quantity'].append(si.initial_quantity() / si.delivered_quantity)
            data['item_name'].append(si.verbose_name or si.cryptic_name)
            # Cannot use pack_cost directly as items using total_weight put the per lb price there.
            data['pack_cost'].append(si.extended_cost / si.delivered_quantity)
            data['source'].append(si.source.name)
        data['item_names'] = ", ".join(data['item_names'])
        return response.Response(data)
