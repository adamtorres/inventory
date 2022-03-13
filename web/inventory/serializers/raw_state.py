from rest_framework import serializers
from rest_framework_recursive import fields

from scrap import serializers as sc_serializers


class RawStateNoRecursionSerializer(sc_serializers.UUIDModelSerializer):
    name = sc_serializers.CharField(allow_blank=False)
    description = sc_serializers.CharField()
    value = serializers.IntegerField(allow_null=False)
    next_state = serializers.SlugRelatedField('name', read_only=True)
    next_error_state = serializers.SlugRelatedField('name', read_only=True)
    failed = serializers.BooleanField()


class RawStateSerializer(sc_serializers.UUIDModelSerializer):
    # Tried the RecursiveField from rest_framework_recursive but kept hitting maximum recursion depth errors.
    name = sc_serializers.CharField(allow_blank=False)
    description = sc_serializers.CharField()
    value = serializers.IntegerField(allow_null=False)
    next_state = RawStateNoRecursionSerializer()
    next_error_state = RawStateNoRecursionSerializer()
    failed = serializers.BooleanField()
