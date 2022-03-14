from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class RawIncomingItemFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="total_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="total_price", lookup_expr='lte')
    partial_name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    delivery_date_range = filters.DateRangeFilter(field_name="delivery_date")

    class Meta:
        model = inv_models.RawIncomingItem
        fields = ['order_number', 'category', 'source', 'name', 'delivery_date', 'partial_name']


class RawIncomingItemView(generics.ListAPIView):
    queryset = inv_models.RawIncomingItem.objects.all()
    model = inv_models.RawIncomingItem
    serializer_class = inv_serializers.RawIncomingItemSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = RawIncomingItemFilter
