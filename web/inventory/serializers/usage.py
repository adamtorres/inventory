from rest_framework import serializers

from inventory import models as inv_models
from scrap import serializers as sc_serializers
from .item_in_stock import ItemInStockSerializer


class UsageSerializer(serializers.ModelSerializer):
    item_in_stock = ItemInStockSerializer()
    previous_unit_quantity = serializers.SerializerMethodField()
    previous_count_quantity = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.Usage
        fields = '__all__'

    def get_previous_count_quantity(self, obj):
        return obj.previous_count_quantity

    def get_previous_unit_quantity(self, obj):
        return obj.previous_unit_quantity


class CreateUsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.Usage
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        # Why isn't this run? UsageCartView.post does the following couple of lines:
        # ui_s = inv_serializers.CreateUsageSerializer(data=used_items, many=True)
        # if ui_s.is_valid()
        print(f"CreateUsageSerializer.is_valid(raise_exception={raise_exception})")
        print(f"self.initial_data = {self.initial_data}")
        return super().is_valid(raise_exception=raise_exception)


class UsageGroupSerializer(serializers.ModelSerializer):
    usages = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.UsageGroup
        fields = '__all__'

    def get_usages(self, obj):
        return UsageSerializer(obj.usages.all(), many=True).data
