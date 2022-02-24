from rest_framework import renderers, response, views

from inventory import models as inv_models, serializers as inv_serializers


class AutocompleteView(views.APIView):
    """
    Given 'terms' on the GET querystring, call the Item's autocomplete_search function.
    """
    def get_queryset(self):
        return inv_models.Item.objects.none()

    def get(self, request, format=None):
        terms = (request.GET.get('terms') or '').split()
        qs = self.get_queryset().model.objects.autocomplete_search(terms)
        qs_data = inv_serializers.ItemSerializer(qs, many=True)
        return response.Response(qs_data.data)


class AutocompleteCommonItemView(views.APIView):
    """
    Given 'terms' on the GET querystring, call the CommonItem's autocomplete_search function.
    """
    def get_queryset(self):
        return inv_models.CommonItem.objects.none()

    def get(self, request, format=None):
        terms = (request.GET.get('terms') or '').split()
        qs = self.get_queryset().model.objects.autocomplete_search(terms)
        qs_data = inv_serializers.CommonItemSerializer(qs, many=True)
        return response.Response(qs_data.data)
