from rest_framework import serializers

from .. import models as inv_models


class SourceItemWideFilterSerializer(serializers.ModelSerializer):
    source_name = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.SourceItem
        fields = [
            "delivered_date",
            "source",
            "source_name",
            "brand",
            "order_number",
            # "po_text",
            "line_item_number",
            "source_category",
            "cryptic_name", "verbose_name", "common_name",
            "item_code", "delivered_quantity",
            "pack_cost", "pack_quantity",
            "unit_quantity", "unit_size",
            "extended_cost", "total_weight", "individual_weights",
            "extra_notes", "extra_code", "scanned_filename",
        ]

    def get_source_name(self, obj):
        return obj.source.name
