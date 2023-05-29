import json
import logging

from rest_framework import response, views

from .. import models as inv_models, serializers as inv_serializers

logger = logging.getLogger(__name__)


class APIChartDataView(views.APIView):
    serializer = inv_serializers.SourceItemGraphDataSerializer

    def get(self, request, format=None):
        # TODO: Consider custom renderer - https://www.django-rest-framework.org/api-guide/renderers/#custom-renderers
        # qs = inv_models.SourceItem.objects.wide_filter([('item_code', ('2105773',)), ('name', ('egg', )), ('source', ('sysco',))])
        # qs = inv_models.SourceItem.objects.wide_filter([('item_code', ('4109518',)), ('name', ('beet', )), ('source', ('sysco',))])
        # qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('8oz',)), ('name', ('milk', 'white'))])
        # qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('8oz',)), ('name', ('milk', 'choc')), ('source', ('sysco', 'rsm'))])
        # qs = inv_models.SourceItem.objects.wide_filter([('name', ('string', 'cheese'))])
        qs = inv_models.SourceItem.objects.wide_filter([('unit_size', ('50lb',)), ('name', ('all', 'flour'))])

        qs = qs.exclude(delivered_quantity__lte=0)
        qs = qs.order_by().order_by('delivered_date', 'source_id', 'order_number', 'line_item_number')
        data = {
            'item_names': set(),
            'item_name': [], 'delivered_date': [], 'per_use_cost': [], 'initial_quantity': [], 'pack_cost': [],
            'source': [],
        }
        for si in qs:
            data['item_names'].add(f"{si.verbose_name or si.cryptic_name} {si.unit_size}")
            data['delivered_date'].append(si.delivered_date)
            data['per_use_cost'].append(si.per_use_cost())
            data['initial_quantity'].append(si.initial_quantity())
            data['item_name'].append(si.verbose_name or si.cryptic_name)
            # Cannot use pack_cost directly as items using total_weight put the per lb price there.
            data['pack_cost'].append(si.extended_cost / si.delivered_quantity)
            data['source'].append(si.source.name)
        data['item_names'] = ", ".join(data['item_names'])
        return response.Response(data)
