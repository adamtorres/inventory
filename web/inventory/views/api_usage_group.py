from django.db import models
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIUsageGroupListView(generics.ListAPIView):
    queryset = inv_models.UsageGroup.objects.all()
    serializer_class = inv_serializers.UsageGroupSerializer

    def paginate_queryset(self, qs):
        if self.request.query_params.get('paging') == 'off':
            return None
        return super().paginate_queryset(qs)


class APIUsageGroupDetailView(generics.RetrieveAPIView):
    queryset = inv_models.UsageGroup.objects.all()
    serializer_class = inv_serializers.UsageGroupSerializer
