from rest_framework import serializers

from .. import models as inv_models
from ..common import use_type


class SourceItemWideFilterSerializer(serializers.ModelSerializer):
    per_use_cost = serializers.SerializerMethodField()
    remaining_cost = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    source_item_name = serializers.SerializerMethodField()
    use_type_str = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.SourceItem
        fields = [
            "id",
            "delivered_date",
            "source",
            "source_name",
            "brand",
            "order_number",
            "po_text",
            "line_item_number",
            "source_category",
            "source_item_name",
            "cryptic_name",
            "verbose_name",
            "common_name",
            "item_code", "delivered_quantity",
            "pack_cost", "pack_quantity",
            "unit_quantity", "unit_size",
            "extended_cost", "total_weight", "individual_weights",
            "extra_notes", "extra_code", "scanned_filename",
            "remaining_quantity", "remaining_cost", "per_use_cost",
            "use_type", "use_type_str",
        ]

    def get_per_use_cost(self, obj):
        return obj.per_use_cost()

    def get_remaining_cost(self, obj):
        return obj.remaining_cost()

    def get_source_item_name(self, obj):
        return obj.verbose_name or obj.cryptic_name

    def get_source_name(self, obj):
        return obj.source.name

    def get_use_type_str(self, obj):
        return use_type.use_type_to_str(obj.use_type)
