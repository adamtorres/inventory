from rest_framework import renderers, response, views

from incoming import models as inc_models, serializers as inc_serializers


class AutocompleteView(views.APIView):
    def get_queryset(self):
        return inc_models.Item.objects.none()

    def get(self, request, format=None):
        terms = (request.GET.get('terms') or '').split()
        sources = (request.GET.get('sources') or '').split(';')
        if not sources:
            sources = None
        qs = self.get_queryset().model.objects.autocomplete_search(terms, sources=sources)
        qs_data = inc_serializers.ItemSerializer(qs, many=True)
        return response.Response(qs_data.data)
