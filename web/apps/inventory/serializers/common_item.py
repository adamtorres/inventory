from rest_framework import serializers

from scrap import fields


class CommonItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    created = serializers.DateTimeField(read_only=True)
    location = serializers.StringRelatedField()
    category = fields.LimitedStringRelatedField(output_field_names='name')

    quantity = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    extended_price = serializers.DecimalField(max_digits=10, decimal_places=4, read_only=True)
    groups = serializers.IntegerField(read_only=True)
    unit_sizes = serializers.CharField(read_only=True)

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()
