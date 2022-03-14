from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class RawIncomingItemFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="total_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="total_price", lookup_expr='lte')
    partial_name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    # TODO: Look into extending the date range choices
    delivery_date_range = filters.DateRangeFilter(field_name="delivery_date")

    class Meta:
        model = inv_models.RawIncomingItem
        fields = ['order_number', 'category', 'source', 'name', 'delivery_date', 'partial_name']


class APIRawIncomingItemListView(generics.ListAPIView):
    queryset = inv_models.RawIncomingItem.objects.all()
    model = inv_models.RawIncomingItem
    serializer_class = inv_serializers.HyperlinkedRawIncomingItemSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = RawIncomingItemFilter


class APIRawIncomingItemView(views.APIView):
    queryset = inv_models.RawIncomingItem.objects.all()
    model = inv_models.RawIncomingItem
    serializer_class = inv_serializers.HyperlinkedRawIncomingItemSerializer

    def get(self, request, pk=None):
        return response.Response(self.serializer_class(self.model.objects.get(id=pk), context={'request': request}).data)
