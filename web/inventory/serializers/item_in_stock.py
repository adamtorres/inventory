from rest_framework import serializers

from inventory import models as inv_models
from scrap import serializers as sc_serializers


class ItemInStockSerializer(serializers.ModelSerializer):
    source = serializers.SerializerMethodField()
    delivery_date = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    unit_size = serializers.SerializerMethodField()
    pack_quantity = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.ItemInStock
        fields = '__all__'

    def get_source(self, obj):
        return obj.raw_incoming_item.rawitem_obj.source.name

    def get_delivery_date(self, obj):
        return obj.raw_incoming_item.delivery_date

    def get_name(self, obj):
        return obj.raw_incoming_item.name

    def get_unit_size(self, obj):
        return obj.raw_incoming_item.unit_size

    def get_pack_quantity(self, obj):
        return obj.raw_incoming_item.pack_quantity
