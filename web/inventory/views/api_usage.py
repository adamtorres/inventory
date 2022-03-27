from django.db import models
from django_filters import rest_framework as filters
from rest_framework import renderers, response, views, generics

from .. import models as inv_models, serializers as inv_serializers


class APIUsageChangeView(views.APIView):
    queryset = inv_models.ItemInStock.objects.all()

    def get(self, request):
        context = {'used_items': {}}
        item_ids = []
        total_count = 0
        if 'used_items' in request.session:
            # Possibly modifying the dict during the loop so have to save off the keys beforehand.
            keys = list(request.session['used_items'].keys())
            for item_id in keys:
                count = request.session['used_items'][item_id]
                if not count:
                    # Cleaning out the session for empty items.
                    request.session['used_items'].pop(item_id)
                    request.session.modified = True
                else:
                    # context['used_items'][item_id] = count
                    item_ids.append(item_id)
                    total_count += count
        qs = self.queryset.filter(id__in=item_ids).exclude(remaining_unit_quantity__lte=0).order_by(
            'raw_incoming_item__rawitem_obj__category__name',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name__name',
            '-raw_incoming_item__delivery_date')
        context['used_items'] = inv_serializers.ItemInStockSerializer(qs, many=True).data
        for item in context['used_items']:
            item_id = item['id']
            count = request.session['used_items'][item_id]
            item['use_count'] = count
        context['total_used_units'] = total_count
        return response.Response(context)

    def post(self, request, *args, **kwargs):
        for k in request.data.keys():
            if k.startswith("used_items["):
                item_id = k.split('[')[1].strip(']')
                if 'used_items' not in request.session:
                    request.session['used_items'] = {}
                new_value = int(request.data[k])
                if item_id in request.session['used_items']:
                    if not new_value:
                        request.session['used_items'].pop(item_id)
                        request.session.modified = True
                    elif request.session['used_items'][item_id] != new_value:
                        request.session['used_items'][item_id] = new_value
                        request.session.modified = True
                elif new_value:
                    request.session['used_items'][item_id] = new_value
                    request.session.modified = True

        return response.Response({'hello': 'there'})
