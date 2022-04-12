from rest_framework import renderers, response, views, generics

from scrap import models as sc_models, views as sc_views
from .. import models as inv_models, serializers as inv_serializers


class APICategoryView(sc_models.QuerysetExtrasMixin, sc_views.APIGetByID, views.APIView):
    queryset = inv_models.Category.objects.all()
    model = inv_models.Category
    serializer_class = inv_serializers.CategorySerializer
    order_fields = ['name']
