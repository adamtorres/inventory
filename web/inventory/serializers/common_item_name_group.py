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
