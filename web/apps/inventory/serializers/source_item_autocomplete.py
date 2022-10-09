from rest_framework import serializers

from .. import models as inv_models


class SourceItemAutocompleteSerializer(serializers.ModelSerializer):
    source_name = serializers.SerializerMethodField()

    class Meta:
        model = inv_models.SourceItem
        fields = [
            "source",
            "source_name",
            "brand",
            "source_category",
            "cryptic_name",
            "verbose_name",
            "common_name",
            "item_code",
            "pack_quantity",
            "unit_quantity",
            "unit_size",
            "extra_code",
        ]

    def get_source_name(self, obj):
        return obj.source.name
