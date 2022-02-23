from rest_framework import serializers

from scrap import fields


class ItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    common_item = fields.LimitedStringRelatedField(output_field_names='name')
    original_quantity = serializers.DecimalField(max_digits=10, decimal_places=4)
    current_quantity = serializers.DecimalField(max_digits=10, decimal_places=4)
    unit_size = serializers.CharField()
    unit_cost = serializers.DecimalField(max_digits=10, decimal_places=4)
    created = serializers.DateTimeField(read_only=True)
    location = serializers.StringRelatedField()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()
