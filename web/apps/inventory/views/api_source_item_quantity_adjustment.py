import json
import logging

from django import http
from django.contrib import messages
from django.template import RequestContext
from django.template.loader import render_to_string
from django.shortcuts import render

from rest_framework import response, views, exceptions

from inventory import models as inv_models, serializers as inv_serializers, errors


logger = logging.getLogger(__name__)


def render_to_json(request, data):
    return http.HttpResponse(
        json.dumps(data, ensure_ascii=False),
        mimetype=request.is_ajax() and "application/json" or "text/html"
    )


class APISourceItemQuantityAdjustmentView(views.APIView):
    queryset = inv_models.SourceItem.objects.all()

    def put(self, request, *args, **kwargs):
        adjusted_pack_quantity = 0
        use_pack_quantity = 0
        adjusted_count_quantity = 0
        use_count_quantity = 0
        obj = None
        resp_data = {'id': None, 'previous': 0, 'adjustment': 0, 'new': 0}
        try:
            adjusted_pack_quantity = int(request.data['remaining_pack_quantity'])
            use_pack_quantity = int(request.data['use_pack_quantity'])
            adjusted_count_quantity = int(request.data['remaining_count_quantity'])
            use_count_quantity = int(request.data['use_count_quantity'])
        except ValueError:
            messages.error(request, "Bad value in arguments.")
            resp_data['msg'] = render(request, 'messages.html').content
            # return exceptions.ValidationError("Bad value in arguments")
            return response.Response(resp_data)
        resp_data['id'] = request.data['item_id']
        resp_data['previous_pack'] = adjusted_pack_quantity
        resp_data['new_pack'] = adjusted_pack_quantity
        resp_data['adjustment_pack'] = use_pack_quantity
        resp_data['previous_count'] = adjusted_count_quantity
        resp_data['new_count'] = adjusted_count_quantity
        resp_data['adjustment_count'] = use_count_quantity
        if (use_pack_quantity == 0) and (use_count_quantity == 0):
            # Noop.  Don't hit database.
            messages.info(request, "No change to quantity.")
            resp_data['msg'] = render(request, 'messages.html').content
            return response.Response(resp_data)

        try:
            # { 'item_id': 'c69db32e-3cd1-4658-812b-d91615ac2950',
            #   'remaining_pack_quantity': '1',
            #   'remaining_count_quantity': '1',
            #   'use_pack_quantity': '0',
            #   'use_count_quantity': '0',
            #   'use_type': 'BU'}
            obj = self.queryset.get(id=request.data['item_id'])
        except self.queryset.model.DoesNotExist:
            messages.error(request, "Specified item not found.")
            resp_data['msg'] = render(request, 'messages.html').content
            # return exceptions.NotFound()
            return response.Response(resp_data)
        except self.queryset.model.MultipleObjectsReturned:
            messages.error(request, "Multiple items returned.  Somehow.  Even though using the primary key.")
            resp_data['msg'] = render(request, 'messages.html').content
            # return exceptions.ValidationError("Multiple objects returned")
            return response.Response(resp_data)

        try:
            obj.adjust_quantity(
                request.data['use_type'], adjusted_pack_quantity, use_pack_quantity, adjusted_count_quantity,
                use_count_quantity)
        except errors.InsufficientQuantityError as ex:
            messages.error(request, str(ex))
            resp_data['msg'] = render(request, 'messages.html').content
            return response.Response(resp_data)
        resp_data['new_pack'] = obj.remaining_pack_quantity
        resp_data['new_count'] = obj.remaining_count_quantity
        messages.success(
            request,
            f"Adjusted quantity from {resp_data['previous_pack']}/{resp_data['previous_count']} by "
            f"{-1 * resp_data['adjustment_pack']}/{-1 * resp_data['adjustment_count']} to {resp_data['new_pack']}/"
            f"{resp_data['new_count']}.")
        resp_data['msg'] = render(request, 'messages.html').content

        return response.Response(resp_data)
