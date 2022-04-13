from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIDepartmentView(generics.ListAPIView):
    queryset = inv_models.Department.objects.all()
    serializer_class = inv_serializers.DepartmentSerializer
    pagination_class = None
