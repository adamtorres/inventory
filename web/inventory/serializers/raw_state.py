from rest_framework import serializers
from rest_framework_recursive import fields

from scrap import serializers as sc_serializers


class RawStateNoRecursionSerializer(sc_serializers.UUIDModelSerializer):
    name = sc_serializers.CharField(allow_blank=False)
    # description = sc_serializers.CharField()
    description = serializers.SerializerMethodField()
    value = serializers.IntegerField(allow_null=False)
    # next_state = serializers.SlugRelatedField('name', read_only=True)
    # next_error_state = serializers.SlugRelatedField('name', read_only=True)
    next_state = serializers.SerializerMethodField()
    next_error_state = serializers.SerializerMethodField()
    failed = serializers.BooleanField()

    def get_description(self, obj):
        print(f"get_description({obj})")
        return obj.description

    def get_next_state(self, obj):
        print(f"get_next_state({obj})")
        if obj.next_state:
            return obj.next_state.name
        return None

    def get_next_error_state(self, obj):
        print(f"get_next_error_state({obj})")
        if obj.next_error_state:
            return obj.next_error_state.name
        return None

    def run_validators(self, value):
        print(f"RawStateNoRecursionSerializer.run_validators({value}")
        return super().run_validators(value)

    def to_internal_value(self, data):
        print(f"RawStateNoRecursionSerializer.to_internal_value({data}")
        data_after = super().to_internal_value(data)
        print(f"\t_writable_fields = {list(self._writable_fields)}")
        print(f"\tto_internal_value({data_after}")
        return data_after

    def to_representation(self, instance):
        # Not being called when .is_valid/.validated_data used
        print(f"RawStateNoRecursionSerializer.to_representation({instance}")
        return super().to_representation(instance)


class RawStateSerializer(sc_serializers.UUIDModelSerializer):
    # Tried the RecursiveField from rest_framework_recursive but kept hitting maximum recursion depth errors.
    name = sc_serializers.CharField(allow_blank=False)
    description = sc_serializers.CharField()
    value = serializers.IntegerField(allow_null=False)
    # next_state = RawStateNoRecursionSerializer()
    # next_error_state = RawStateNoRecursionSerializer()
    next_state = serializers.SerializerMethodField()
    next_error_state = serializers.SerializerMethodField()
    failed = serializers.BooleanField()

    def get_next_state(self, obj):
        if obj.next_state:
            return {
                "id": obj.id,
                "name": obj.name,
                "description": obj.description,
                "value": obj.value,
                "next_state": obj.next_state.name,
                "next_error_state": obj.next_error_state.name,
                "failed": obj.failed,
            }

            print(f"RawStateSerializer.get_next_state: name={obj.name}, next_state.name={obj.next_state.name}")
            return RawStateNoRecursionSerializer(obj.next_state).data
            # s = RawStateNoRecursionSerializer(
            #     data={
            #         "id": obj.id,
            #         "name": obj.name,
            #         "description": obj.description,
            #         "value": obj.value,
            #         "next_state": obj.next_state,
            #         "next_error_state": obj.next_error_state,
            #         "failed": obj.failed,
            #     }
            # )
            # print(f"get_next_state({obj})")
            # # for field in s._readable_fields:
            # #     print(f"field.field_name = {field.field_name}")
            # s.is_valid()
            # return s.validated_data
            # # return obj.next_state.name
        return None

    def get_next_error_state(self, obj):
        if obj.next_error_state:
            # Passing the instance to the serializer still caused a pile of extra queries.
            # Passing the manually built data dict gets around that.
            return {
                "id": obj.id,
                "name": obj.name,
                "description": obj.description,
                "value": obj.value,
                "next_state": obj.next_state.name,
                "next_error_state": obj.next_error_state.name,
                "failed": obj.failed,
            }
            print(f"RawStateSerializer.get_next_error_state: name={obj.name}, next_state.name={obj.next_error_state.name}")
            return RawStateNoRecursionSerializer(obj.next_error_state).data
            # s = RawStateNoRecursionSerializer(
            #     data={
            #         "id": obj.id,
            #         "name": obj.name,
            #         "description": obj.description,
            #         "value": obj.value,
            #         "next_state": obj.next_state,
            #         "next_error_state": obj.next_error_state,
            #         "failed": obj.failed,
            #     }
            # )
            # s.is_valid()
            # return s.validated_data
            # # return obj.next_error_state.name
        return None
