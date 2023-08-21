import json
import logging

from rest_framework import response, views, exceptions

from .. import models as mkt_models


logger = logging.getLogger(__name__)


class APIOrderModifyDateView(views.APIView):
    queryset = mkt_models.Order.objects.all()

    def put(self, request, *args, **kwargs):
        resp_data = {"hello": "world", "action": kwargs.get("action"), "pk": kwargs.get("pk")}
        logger.debug(f"APIOrderModifyDateView.put: resp_data = {json.dumps(resp_data, default=str, sort_keys=True)}")
        return response.Response(resp_data)
