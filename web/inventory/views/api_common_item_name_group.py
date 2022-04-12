from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from scrap import models as sc_models, views as sc_views
from .. import models as inv_models, serializers as inv_serializers


class APICommonItemNameGroupView(sc_models.QuerysetExtrasMixin, sc_views.APIGetByID, views.APIView):
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
