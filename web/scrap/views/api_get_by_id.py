from rest_framework import renderers, response, views, generics


class APIGetByID:
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
