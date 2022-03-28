from rest_framework import serializers

from inventory import models as inv_models
from scrap import serializers as sc_serializers
from .item_in_stock import ItemInStockSerializer


class UsageSerializer(serializers.ModelSerializer):
    item_in_stock = ItemInStockSerializer()
    previous_unit_quantity = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.Usage
        fields = '__all__'

    def get_previous_unit_quantity(self, obj):
        return obj.previous_unit_quantity


class CreateUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.Usage
        fields = '__all__'


class UsageGroupSerializer(serializers.ModelSerializer):
    usages = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.UsageGroup
        fields = '__all__'

    def get_usages(self, obj):
        return UsageSerializer(obj.usages.all(), many=True).data
