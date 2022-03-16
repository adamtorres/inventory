from django.db import models
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class RawIncomingOrderFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name="total_price", lookup_expr='gte')
    max_price = filters.NumberFilter(field_name="total_price", lookup_expr='lte')
    partial_name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    # TODO: Look into extending the date range choices
    delivery_date_range = filters.DateRangeFilter(field_name="delivery_date")

    class Meta:
        model = inv_models.RawIncomingItem
        fields = ['delivery_date', 'source', 'order_number', 'category', 'name', 'partial_name']

    def filter_queryset(self, queryset):
        qs = super().filter_queryset(queryset)
        qs = qs.distinct('delivery_date', 'source', 'order_number')
        order_filter = models.Q()
        for order in qs:
            order_filter = order_filter | models.Q(
                delivery_date=order.delivery_date, source=order.source, order_number=order.order_number)
        return self.Meta.model.objects.orders().filter(order_filter)


class APIRawIncomingOrderListView(generics.ListAPIView):
    queryset = inv_models.RawIncomingItem.objects.all()
    model = inv_models.RawIncomingItem
    filter_backends = [filters.DjangoFilterBackend]
    filter_class = RawIncomingOrderFilter

    def paginate_queryset(self, qs):
        print(f"APIRawIncomingOrderListView.paginate_queryset: query_params = {self.request.query_params}")
        if self.request.query_params.get('paging') == 'off':
            return None
        return super().paginate_queryset(qs)

    def get_serializer_class(self):
        if self.request.query_params.get('format') == 'json':
            # TODO: a hyperlinked order serializer
            return inv_serializers.RawIncomingOrderSerializer
        return inv_serializers.RawIncomingOrderSerializer


class APIRawIncomingOrderDetailView(generics.GenericAPIView):
    queryset = inv_models.RawIncomingItem.objects.orders()
    model = inv_models.RawIncomingItem

    def get_serializer_class(self):
        if self.request.query_params.get('format') == 'json':
            return inv_serializers.RawIncomingOrderSerializer
        return inv_serializers.RawIncomingOrderSerializer

    def get_object(self):
        return self.model.objects.orders(item_id=self.kwargs.get('pk')).first()

    def get(self, request, pk=None):
        serializer_class = self.get_serializer_class()
        order = self.get_object()
        obj = serializer_class(order, context={'request': request}, include_items=True)
        return response.Response(obj.data)
