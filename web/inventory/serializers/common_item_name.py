from rest_framework import serializers

from .. import models as inv_models


class CommonItemNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.CommonItemName
        fields = '__all__'
