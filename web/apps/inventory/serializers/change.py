from rest_framework import serializers

from .. import models as inv_models


class ChangeSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    class Meta:
        model = inv_models.Change
        fields = ['created', 'action_date', 'applied_datetime']
