from django.views import generic
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from scrap import models as sc_models, views as sc_views
from .. import models as inv_models, serializers as inv_serializers


class APISupportingDataView(views.APIView):
    """
    Returns a variety of data in one call instead of multiple calls.
    """

    def get(self, request, *args, **kwargs):
        context = {
            'categories': self.get_categories(),
            'departments': self.get_departments(),
            'sources': self.get_sources(),
        }
        return response.Response(context)

    def get_categories(self):
        queryset = inv_models.Category.objects.all()
        serializer_class = inv_serializers.CategorySerializer
        return serializer_class(queryset, many=True).data

    def get_departments(self):
        queryset = inv_models.Department.objects.all()
        serializer_class = inv_serializers.DepartmentSerializer
        return serializer_class(queryset, many=True).data

    def get_sources(self):
        queryset = inv_models.Source.objects.all()
        serializer_class = inv_serializers.SourceSerializer
        return serializer_class(queryset, many=True).data
