from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIItemInStockView(views.APIView):
    """
    Returns a single or list of ItemInStock with a select few extra values added from raw_incoming_item and source.
    """
    queryset = inv_models.ItemInStock.objects.none()
    model = inv_models.ItemInStock
    serializer_class = inv_serializers.ItemInStockSerializer

    def get(self, request, pk=None):
        if pk:
            object = self.model.objects.get(id=pk)
            return response.Response(self.serializer_class(object, many=False).data)
        id_list = request.GET.getlist('id')
        if not id_list:
            id_list = request.GET.getlist('id[]')
        object_list = self.model.objects.filter(id__in=id_list).exclude(remaining_unit_quantity__lte=0).order_by('-raw_incoming_item__delivery_date')
        return response.Response(self.serializer_class(object_list, many=True).data)
