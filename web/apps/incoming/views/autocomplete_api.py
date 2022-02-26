from rest_framework import renderers, response, views

from incoming import models as inc_models, serializers as inc_serializers


class AutocompleteView(views.APIView):
    """
    Given 'terms' and 'sources' on the GET querystring, call the Item's autocomplete_search function.
    """
    model = None
    serializer = None

    def get_queryset(self):
        return self.model.objects.none()

    def get(self, request, format=None):
        terms = (request.GET.get('terms') or '').split()
        sources = (request.GET.get('sources') or '').split()
        if not sources:
            sources = None
        qs = self.get_queryset().model.objects.autocomplete_search(terms, sources=sources)
        qs_data = self.serializer(qs, many=True)
        return response.Response(qs_data.data)


class AutocompleteItemView(AutocompleteView):
    model = inc_models.Item
    serializer = inc_serializers.ItemSerializer


class AutocompleteIncomingItemsView(AutocompleteView):
    model = inc_models.IncomingItem
    serializer = inc_serializers.IncomingItemSerializer
