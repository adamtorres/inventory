from rest_framework import response, views


class WideFilterView(views.APIView):
    model = None
    serializer = None
    prefetch_fields = None

    def get_queryset(self):
        return self.model.objects.none()

    def get(self, request, format=None):
        # wide_filter_fields = list of GET keys to look for.  So other args can be used and not get in the way.
        # /inventory/api_rawitem/wide_filter/?wide_filter_fields=name&name=beef+ground&empty=false
        filter_fields = request.GET.getlist('wide_filter_fields')
        filter_fields_and_values = []
        for filter_field in filter_fields:
            filter_tuple = ()
            if filter_field in request.GET:
                filter_tuple = (filter_field, (request.GET.get(filter_field) or '').split())
            if f"{filter_field}[]" in request.GET:
                # TODO: this doesn't call split.  Does that mean these can include spaces?
                filter_tuple = (filter_field, (request.GET.getlist(f"{filter_field}[]") or []))
            if filter_tuple:
                filter_fields_and_values.append(filter_tuple)
        if (request.GET.get('empty') or 'true') == 'true':
            # Shortcut an empty filter request.  We could send back a sample set, all, or none.
            return response.Response(self.serializer(self.get_queryset(), many=True).data)
        # wide_filter expects
        # search_terms = [
        #     ('name', ('ground', 'beef')),
        #     ('category', 'meats'),
        # ]
        data = self.serializer(self.filter_qs(filter_fields_and_values), many=True).data
        return response.Response(data)

    def filter_qs(self, search_terms):
        qs = self.model.objects.wide_filter(search_terms)
        qs = self.prefetch_qs(qs)
        return qs

    def prefetch_qs(self, qs):
        if self.prefetch_fields:
            return qs.prefetch_related(*self.prefetch_fields)
        return qs
