from rest_framework import serializers


class UUIDModelSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()
