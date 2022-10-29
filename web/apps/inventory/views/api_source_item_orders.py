import logging

from rest_framework import response, views

from scrap import utils
from inventory import models as inv_models, serializers as inv_serializers


logger = logging.getLogger(__name__)


class APISourceItemOrdersView(views.APIView):
    def get(self, request, format=None):
        source_ids = request.GET.getlist('source_id')
        source_names = request.GET.getlist('source')
        order_number = request.GET.getlist('order_number')
        delivered_date = request.GET.getlist('delivered_date')
        qs = inv_models.SourceItem.objects.order_list(
            source_id=source_ids, source_name=source_names, delivered_date=delivered_date, order_number=order_number)
        data = inv_serializers.SourceItemOrderSerializer(qs, many=True).data
        return response.Response(data)

