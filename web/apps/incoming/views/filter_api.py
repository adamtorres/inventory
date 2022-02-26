from rest_framework import renderers, response, views

from incoming import models as inc_models, serializers as inc_serializers


class FilterView(views.APIView):
    """
    Given 'terms' and 'sources' on the GET querystring, call the Item's autocomplete_search function.
    """
    model = None
    serializer = None

    def get_queryset(self):
        return self.model.objects.none()

    def get(self, request, format=None):
        filter_fields = request.GET.getlist('filter_fields[]')
        print(f"FilterIncomingItemsView.get(): filter_fields = {filter_fields!r}")
        filter_fields_and_values = {}
        for filter_field in filter_fields:
            filter_fields_and_values[filter_field] = (request.GET.get(filter_field) or '').split()
        if (request.GET.get('empty') or 'true') == 'true':
            print(f"Interpreted '{request.GET.get('empty')}' as True.")
            return response.Response(self.serializer(self.get_queryset(), many=True).data)
        print(f"filter_fields_and_values = {filter_fields_and_values}")
        qs = self.get_queryset().model.objects.all()[:5]
        qs_data = self.serializer(qs, many=True)
        data = qs_data.data
        # data = [{
        #     "id": "00000000-0000-0000-0000-000000000000",
        #     "created": "value for created",
        #     "ordered_quantity": "value for ordered_quantity",
        #     "delivered_quantity": "value for delivered_quantity",
        #     "total_weight": "value for total_weight",
        #     "pack_price": "value for pack_price",
        #     "pack_tax": "value for pack_tax",
        #     "extended_price": "value for extended_price",
        #     "line_item_position": "value for line_item_position",
        #     "comment": "value for comment",
        #     "parent": "value for parent",
        #     "item": "value for item",
        # }]
        return response.Response(data)


class FilterItemView(FilterView):
    model = inc_models.Item
    serializer = inc_serializers.ItemSerializer


class FilterIncomingItemsView(FilterView):
    model = inc_models.IncomingItem
    serializer = inc_serializers.IncomingItemSerializer
