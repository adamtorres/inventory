from rest_framework import serializers

from .. import models as inv_models
from .category import CategorySerializer
from .common_item_name_group import CommonItemNameGroupSerializer
from .source import SourceSerializer


class RawItemSerializer(serializers.ModelSerializer):
    source = SourceSerializer()
    category = CategorySerializer()
    common_item_name_group = CommonItemNameGroupSerializer()

    class Meta:
        model = inv_models.RawItem
        fields = '__all__'

# TODO: add a Flat serializer to be used by wide_filter.
