from rest_framework import serializers

from .uuid_model import UUIDModelSerializer


class DatedModelSerializer(UUIDModelSerializer):
    created = serializers.DateTimeField(read_only=True)
    modified = serializers.DateTimeField(read_only=True)

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        raise NotImplementedError()
