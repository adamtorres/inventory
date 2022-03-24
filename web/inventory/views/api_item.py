from django.db import models
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIItemWithInStockQuantities(views.APIView):
    queryset = inv_models.Item.objects.none()
    model = inv_models.Item
    serializer_class = inv_serializers.ItemWithInStockQuantitiesSerializer

    def get(self, request):
        object_list = inv_models.Item.objects.with_in_stock_quantities()
        return response.Response(self.serializer_class(object_list, many=True).data)
