import json

from django.db import models
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIUsageChangeView(views.APIView):
    queryset = inv_models.ItemInStock.objects.all()

    def get(self, request):
        context = {'used_items': {}}
        item_ids = []
        total_unit_count = 0
        total_count_count = 0
        if 'used_items' in request.session:
            # Possibly modifying the dict during the loop so have to save off the keys beforehand.
            keys = list(request.session['used_items'].keys())
            for item_id in keys:
                x = request.session['used_items'][item_id]
                count = x['value']
                count_type = x['value_type']
                if not count:
                    # Cleaning out the session for empty items.
                    request.session['used_items'].pop(item_id)
                    request.session.modified = True
                else:
                    # context['used_items'][item_id] = count
                    item_ids.append(item_id)
                    if count_type == 'unit':
                        total_unit_count += count
                    else:
                        total_count_count += count
        qs = self.queryset.filter(id__in=item_ids).exclude(remaining_unit_quantity__lte=0).order_by(
            'raw_incoming_item__rawitem_obj__category__name',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name__name',
            '-raw_incoming_item__delivery_date')
        context['used_items'] = inv_serializers.ItemInStockSerializer(qs, many=True).data
        for item in context['used_items']:
            item_id = item['id']
            x = request.session['used_items'][item_id]
            count = x['value']
            count_type = x['value_type']
            item['use_count'] = count
            item['use_count_type'] = count_type
            if count_type == 'unit':
                item['use_price'] = round(int(count) * float(item['unit_price']), 4)
            else:
                item['use_price'] = round(int(count) * float(item['count_price']), 4)
        context['total_used_units'] = total_unit_count
        context['total_used_count'] = total_count_count
        return response.Response(context)

    def post(self, request, *args, **kwargs):
        if 'empty_cart' in request.data:
            if 'used_items' in request.session and request.session['used_items']:
                request.session['used_items'] = {}
                request.session.modified = True
            return response.Response({'hello': 'there'})
        if 'used_items' in request.data:
            for item_id in request.data['used_items']:
                if 'used_items' not in request.session:
                    request.session['used_items'] = {}
                new_value_and_type = request.data['used_items'][item_id]
                new_value = int(new_value_and_type['value'])
                new_value_type = new_value_and_type['value_type']
                if item_id in request.session['used_items']:
                    if not new_value:
                        request.session['used_items'].pop(item_id)
                        request.session.modified = True
                    elif (
                            (request.session['used_items'][item_id]['value'] != new_value) or
                            (request.session['used_items'][item_id]['value_type'] != new_value_type)):
                        request.session['used_items'][item_id] = {'value': new_value, 'value_type': new_value_type}
                        request.session.modified = True
                elif new_value:
                    request.session['used_items'][item_id] = {'value': new_value, 'value_type': new_value_type}
                    request.session.modified = True
        return response.Response({'hello': 'there'})


class APIUsageCreateView(generics.CreateAPIView):
    queryset = inv_models.UsageGroup
    serializer_class = inv_serializers.UsageGroupSerializer

