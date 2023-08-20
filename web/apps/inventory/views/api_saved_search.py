import logging

from rest_framework import response, views

from inventory import models as inv_models


logger = logging.getLogger(__name__)


class APISavedSearchView(views.APIView):
    def get(self, request, pk=None, format=None):
        obj = inv_models.SearchCriteria.objects.get(pk=pk)
        return response.Response(obj.criteria)
