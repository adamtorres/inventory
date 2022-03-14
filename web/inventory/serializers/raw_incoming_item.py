from rest_framework import serializers

from scrap import serializers as sc_serializers
from .raw_state import RawStateSerializer


class RawIncomingItemSerializer(sc_serializers.DatedModelSerializer):
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

    line_item_position = serializers.IntegerField(allow_null=True)

    category = sc_serializers.CharField(allow_blank=False)
    name = sc_serializers.CharField(allow_blank=False)

    ordered_quantity = sc_serializers.DecimalField()
    delivered_quantity = sc_serializers.DecimalField()
    item_code = sc_serializers.CharField()
    extra_code = sc_serializers.CharField()
    unit_size = sc_serializers.CharField()
    total_weight = sc_serializers.DecimalField()
    pack_quantity = sc_serializers.DecimalField()
    pack_price = sc_serializers.MoneyField()
    pack_tax = sc_serializers.MoneyField()
    extended_price = sc_serializers.MoneyField()

    item_comment = sc_serializers.CharField()
    scanned_image_filename = sc_serializers.CharField()

    state = RawStateSerializer()
    failure_reason = sc_serializers.CharField(allow_null=True, allow_blank=True)
    # def update(self, instance, validated_data):
    #     raise NotImplementedError()
    #
    # def create(self, validated_data):
    #     raise NotImplementedError()
