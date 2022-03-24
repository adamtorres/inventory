from rest_framework import serializers

from scrap import serializers as sc_serializers


class UnitSizeWithQuantitySerializer(serializers.Serializer):
    unit_size = sc_serializers.CharField()
    pack_quantity = sc_serializers.DecimalField()


class ItemWithInStockQuantitiesSerializer(serializers.Serializer):
    source = serializers.SerializerMethodField()
    name = sc_serializers.CharField()
    quantities = UnitSizeWithQuantitySerializer(many=True)

    def get_source(self, obj):
        if 'source' in obj:
            return obj['source']
        return ""
