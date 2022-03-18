from rest_framework import serializers

from .. import models as inv_models


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.Category
        fields = '__all__'
