from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APICommonItemNameGroupView(views.APIView):
    """
    Returns a single or list of CommonItemNameGroup.
    """
    queryset = inv_models.CommonItemNameGroup.objects.all()
    model = inv_models.CommonItemNameGroup
    serializer_class = inv_serializers.CommonItemNameGroupWideFilterSerializer
    order_fields = ['name__name']
    prefetch_fields = [
        'names',
        'raw_items', 'raw_items__category', 'raw_items__raw_incoming_items',
        'raw_items__raw_incoming_items__source_obj'
    ]

    def get(self, request, pk=None):
        if pk:
            obj = self.model.objects.get(id=pk)
            return response.Response(self.serializer_class(obj, many=False).data)
        id_list = request.GET.getlist('id')
        if not id_list:
            id_list = request.GET.getlist('id[]')
        if id_list:
            object_list = self.model.objects.filter(id__in=id_list)
        else:
            object_list = self.queryset
        object_list = self.order_qs(self.prefetch_qs(object_list))
        return response.Response(self.serializer_class(object_list, many=True).data)

    def order_qs(self, qs):
        if self.order_fields:
            return qs.order_by().order_by(*self.order_fields)

    def prefetch_qs(self, qs):
        if self.prefetch_fields:
            return qs.prefetch_related(*self.prefetch_fields)
        return qs
