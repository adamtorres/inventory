from django.db import models
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIItemWithInStockQuantities(views.APIView):
    """
    In Stock inventory based on source-provided names.
    "firecls beef grnd bulk 81/19 chub f" vs. "ground beef"
    """
    queryset = inv_models.Item.objects.none()
    model = inv_models.Item
    serializer_class = inv_serializers.SourceItemWithInStockQuantitiesSerializer

    def get(self, request):
        object_list = self.model.objects.with_in_stock_quantities()
        return response.Response(self.serializer_class(object_list, many=True).data)


class APICommonItemWithInStockQuantities(views.APIView):
    """
    In Stock inventory based on common names.
    "ground beef" vs. "firecls beef grnd bulk 81/19 chub f"
    """
    queryset = inv_models.CommonItemNameGroup.objects.none()
    model = inv_models.CommonItemNameGroup
    serializer_class = inv_serializers.ItemWithInStockQuantitiesSerializer

    def get(self, request, pk=None):
        qs = None
        if pk:
            qs = self.model.objects.filter(id=pk)
        object_list = self.model.objects.with_in_stock_quantities(qs=qs)
        return response.Response(self.serializer_class(object_list, many=True).data)
