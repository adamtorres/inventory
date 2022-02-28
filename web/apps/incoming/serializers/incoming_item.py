from rest_framework import serializers


class IncomingItemSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    created = serializers.DateTimeField(read_only=True)

    ordered_quantity = serializers.DecimalField(max_digits=10, decimal_places=4)
    delivered_quantity = serializers.DecimalField(max_digits=10, decimal_places=4)
    total_weight = serializers.DecimalField(max_digits=10, decimal_places=4)
    pack_quantity = serializers.SerializerMethodField()
    unit_size = serializers.SerializerMethodField()
    pack_price = serializers.DecimalField(max_digits=10, decimal_places=4)
    pack_tax = serializers.DecimalField(max_digits=10, decimal_places=4)
    extended_price = serializers.DecimalField(max_digits=10, decimal_places=4)
    line_item_position = serializers.IntegerField()

    comment = serializers.CharField()
    item_comment = serializers.SerializerMethodField()

    parent = serializers.StringRelatedField()
    department = serializers.SerializerMethodField()
    item = serializers.StringRelatedField()
    common_name = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()

    def get_common_name(self, obj):
        return obj.item.common_item.name

    def get_department(self, obj):
        return obj.parent.department.name

    def get_item_comment(self, obj):
        return obj.item.comment

    def get_pack_quantity(self, obj):
        return obj.item.pack_quantity

    def get_unit_size(self, obj):
        return obj.item.unit_size
