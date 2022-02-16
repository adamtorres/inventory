from rest_framework import serializers


class ItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)
    identifier = serializers.CharField()
    name = serializers.CharField()
    better_name = serializers.CharField()
    do_not_inventory = serializers.BooleanField()
    discontinued = serializers.BooleanField()
    pack_quantity = serializers.DecimalField(max_digits=10, decimal_places=4)
    unit_size = serializers.CharField()

    source = serializers.StringRelatedField()
    common_item = serializers.StringRelatedField()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()
