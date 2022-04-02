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
    common_name = serializers.SerializerMethodField()
    uncommon_item_names = serializers.SerializerMethodField()
    common_names = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    sources = serializers.SerializerMethodField()
    unit_sizes = serializers.SerializerMethodField()
    order_count = serializers.SerializerMethodField()
    remaining_price = serializers.SerializerMethodField()

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
        return obj.order_count

    def get_remaining_price(self, obj):
        return obj.remaining_price
