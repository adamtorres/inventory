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
        filter_fields_and_values = {}
        for filter_field in filter_fields:
            filter_fields_and_values[filter_field] = (request.GET.get(filter_field) or '').split()
        if (request.GET.get('empty') or 'true') == 'true':
            return response.Response(self.serializer(self.get_queryset(), many=True).data)
        return response.Response(self.serializer(self.filter_qs(**filter_fields_and_values), many=True).data)

    def filter_qs(self, **kwargs):
        qs = self.model.objects.live_filter(**kwargs)
        return qs


class FilterItemView(FilterView):
    model = inc_models.Item
    serializer = inc_serializers.ItemSerializer


class FilterIncomingItemsView(FilterView):
    model = inc_models.IncomingItem
    serializer = inc_serializers.IncomingItemSerializer
