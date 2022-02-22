from rest_framework import serializers


class SourceSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    name = serializers.CharField()
    active = serializers.BooleanField()
    created = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()
