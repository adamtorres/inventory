from rest_framework import serializers

from scrap import serializers as sc_serializers
from .. import models as inv_models


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
