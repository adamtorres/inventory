from rest_framework import serializers
from rest_framework.fields import empty

from scrap import serializers as sc_serializers
from .. import models as inv_models
from .raw_incoming_item import RawIncomingItemInOrderSerializer


class RawIncomingOrderSerializer(serializers.Serializer):
    # TODO: order detail page which uses multiple fields to
    # url = serializers.HyperlinkedIdentityField(
    #     view_name='inventory:api_rawincomingitem_detail',
    #     lookup_field='pk'
    # )
    source = sc_serializers.CharField()
    department = sc_serializers.CharField()
    customer_number = sc_serializers.CharField()
    order_number = sc_serializers.CharField()
    po_text = sc_serializers.CharField()
    order_comment = sc_serializers.CharField()
    order_date = serializers.DateField(allow_null=True)
    delivery_date = serializers.DateField(allow_null=True)
    total_price = sc_serializers.MoneyField()
    total_packs = sc_serializers.DecimalField()
    item_count = serializers.IntegerField()
    item_ids = serializers.ListField()
    items = serializers.SerializerMethodField()

    def __init__(self, instance=None, data=empty, **kwargs):
        setattr(self, "include_items", kwargs.pop('include_items', False))
        super().__init__(instance=instance, data=data, **kwargs)

    def get_items(self, obj):
        if self.include_items:
            item_qs = inv_models.RawIncomingItem.objects.filter(id__in=obj['item_ids'])
            item_qs = item_qs.order_by('line_item_position')
            return RawIncomingItemInOrderSerializer(item_qs, many=True).data
        return []
