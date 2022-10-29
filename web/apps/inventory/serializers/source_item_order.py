from rest_framework import serializers


class SourceItemOrderSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    delivered_date = serializers.SerializerMethodField()
    order_number = serializers.SerializerMethodField()
    order_id = serializers.SerializerMethodField()
    sum_extended_cost = serializers.SerializerMethodField()
    count_line_item = serializers.SerializerMethodField()

    def update(self, instance, validated_data):
        raise NotImplementedError("Nope.  Not gonna do it.")

    def create(self, validated_data):
        raise NotImplementedError("Nope.  Not gonna do it.")

    def get_id(self, obj):
        return obj['source']

    def get_source_name(self, obj):
        return obj['source__name']

    def get_order_id(self, obj):
        return obj['order_id']

    def get_order_number(self, obj):
        return obj['order_number']

    def get_delivered_date(self, obj):
        return obj['delivered_date']

    def get_sum_extended_cost(self, obj):
        return obj['sum_extended_cost']

    def get_count_line_item(self, obj):
        return obj['count_line_item']
