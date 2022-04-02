from rest_framework import serializers

from .. import models as inv_models
from .category import CategorySerializer
from .common_item_name import CommonItemNameSerializer


class CommonItemNameGroupSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    name = CommonItemNameSerializer()

    class Meta:
        model = inv_models.CommonItemNameGroup
        fields = '__all__'


class CommonItemNameGroupWideFilterSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    common_name = serializers.SerializerMethodField()  # CING.name.name
    uncommon_item_names = serializers.SerializerMethodField()  # CING.uncommon_item_names.  raw_items__better_name?
    common_names = serializers.SerializerMethodField()  # list of CING.names.name
    categories = serializers.SerializerMethodField()  # list of raw_items__category__name
    sources = serializers.SerializerMethodField()  # list of raw_items__raw_incoming_items__source_obj__name
    unit_sizes = serializers.SerializerMethodField()  # list of raw_items__unit_size
    order_count = serializers.SerializerMethodField()  # Count raw_items__raw_incoming_items__in_stock__id where qty>0
    remaining_price = serializers.SerializerMethodField()  # Sum raw_items__raw_incoming_items__in_stock__remaining*price

    def get_common_name(self, obj):
        return obj.name.name

    def get_uncommon_item_names(self, obj):
        return sorted(obj.uncommon_item_names)

    def get_common_names(self, obj):
        return sorted([n.name for n in obj.names.all() if n.name != obj.name.name])

    def get_categories(self, obj):
        return sorted({ri.category.name for ri in obj.raw_items.all()})

    def get_id(self, obj):
        return obj.id

    def get_sources(self, obj):
        return sorted({rii.source_obj.name for ri in obj.raw_items.all() for rii in ri.raw_incoming_items.all()})

    def get_unit_sizes(self, obj):
        return sorted({ri.unit_size for ri in obj.raw_items.all()})

    def get_order_count(self, obj):
        # Count raw_items__raw_incoming_items__in_stock__id where qty>0
        return obj.order_count

    def get_remaining_price(self, obj):
        return obj.remaining_price
