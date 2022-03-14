from rest_framework import serializers

from scrap import serializers as sc_serializers


class RawStateNoNextStateSerializer(sc_serializers.UUIDModelSerializer):
    """
    Serializes a RawState such that the next states are not included to avoid more database queries.
    This would be used when the passed object is already the next state from the item's current.
    """
    # TODO: if interested, might look into overloading __init__ to determine if this is the first state or nested.
    name = sc_serializers.CharField(allow_blank=False)
    description = sc_serializers.CharField()
    value = serializers.IntegerField(allow_null=False)
    failed = serializers.BooleanField()


class RawStateSerializer(sc_serializers.UUIDModelSerializer):
    name = sc_serializers.CharField(allow_blank=False)
    description = sc_serializers.CharField()
    value = serializers.IntegerField(allow_null=False)
    next_state = RawStateNoNextStateSerializer()
    next_error_state = RawStateNoNextStateSerializer()
    failed = serializers.BooleanField()
