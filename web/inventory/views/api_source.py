from rest_framework import generics

from .. import models as inv_models, serializers as inv_serializers


class APISourceView(generics.ListAPIView):
    queryset = inv_models.Source.objects.all()
    serializer_class = inv_serializers.SourceSerializer
    pagination_class = None
