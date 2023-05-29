from rest_framework import serializers

from .. import models as inv_models


class SourceItemGraphDataSerializer(serializers.ModelSerializer):
    source_name = serializers.SerializerMethodField()
    per_use_cost = serializers.SerializerMethodField()
    initial_quantity = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.SourceItem
        fields = [
            "source",
            "source_name",
            "source_category",
            "cryptic_name",
            "verbose_name",
            "common_name",
            "item_code",
            "pack_quantity",
            "unit_quantity",
            "unit_size",
            "extra_code",
            "id",
            "extended_cost",
            "per_use_cost",
            "delivered_quantity",
            "initial_quantity",
            "delivered_date",
        ]

    def get_initial_quantity(self, obj):
        return obj.initial_quantity()

    def get_per_use_cost(self, obj):
        return obj.per_use_cost()

    def get_source_name(self, obj):
        return obj.source.name
