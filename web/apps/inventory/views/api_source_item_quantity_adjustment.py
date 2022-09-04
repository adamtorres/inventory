import logging

from rest_framework import response, views, exceptions

from scrap import views as sc_views

from inventory import models as inv_models, serializers as inv_serializers


logger = logging.getLogger(__name__)


class SourceItemQuantityAdjustmentView(views.APIView):
    queryset = inv_models.SourceItem.objects.all()

    def put(self, request, *args, **kwargs):
        adjusted_quantity = 0
        use_quantity = 0
        obj = None
        try:
            adjusted_quantity = int(request.data['remaining_quantity'])
            use_quantity = int(request.data['use_quantity'])
        except ValueError:
            return exceptions.ValidationError("Bad value in arguments")

        if use_quantity == 0:
            # Noop.  Don't hit database.
            return response.Response({'id': request.data['item_id'], 'remaining_quantity': adjusted_quantity})

        try:
            # { 'item_id': 'c69db32e-3cd1-4658-812b-d91615ac2950',
            #   'remaining_quantity': '1',
            #   'use_quantity': '0',
            #   'use_type': 'BU'}
            obj = self.queryset.get(id=request.data['item_id'])
        except self.queryset.model.DoesNotExist:
            return exceptions.NotFound()
        except self.queryset.model.MultipleObjectsReturned:
            return exceptions.ValidationError("Multiple objects returned")

        obj.adjust_quantity(request.data['use_type'], adjusted_quantity, use_quantity)

        return response.Response({'id': obj.id, 'remaining_quantity': adjusted_quantity})
