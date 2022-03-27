from rest_framework import serializers

from inventory import models as inv_models
from scrap import serializers as sc_serializers


class UsageGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.UsageGroup
        fields = '__all__'


class UsageSerializer(serializers.ModelSerializer):
    class Meta:
        model = inv_models.Usage
        fields = '__all__'
