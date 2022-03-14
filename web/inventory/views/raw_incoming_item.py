from rest_framework import renderers, response, views

from .. import models as inv_models, serializers as inv_serializers


class BaseView(views.APIView):
    model = None
    serializer = None

    def get_queryset(self):
        return self.model.objects.none()

    def get(self, request, format=None):

        qs = self.get_queryset().model.objects.all()[:5]
        qs_data = self.serializer(qs, many=True)
        return response.Response(qs_data.data)


class RawIncomingItemView(BaseView):
    model = inv_models.RawIncomingItem
    serializer = inv_serializers.RawIncomingItemSerializer
