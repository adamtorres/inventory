from functools import partial
from rest_framework import serializers


class LimitedStringRelatedField(serializers.StringRelatedField):
    output_field_names = None
    output_field_delimiter = None

    def __init__(self, output_field_names: str | list = None, output_field_delimiter: str = ", ", **kwargs):
        """
        The base StringRelatedField simply wraps the related object in str().  Since I'm strange, a number of my models'
        __str__ methods run querysets to build a string from other related objects.  This causes a db call for every
        record returned when the object is used by StringRelatedField.
        This class gets around that by allowing the user to specify a field(s) to use.

        Args:
            output_field_names: A single str or a list of str defining the attributes from the related object to use.
            output_field_delimiter: A str to use when joining the specified attributes.
            **kwargs:
        """
        self.output_field_names = output_field_names
        self.output_field_delimiter = output_field_delimiter
        super().__init__(**kwargs)

    def to_representation(self, value):
        if isinstance(self.output_field_names, str):
            return getattr(value, self.output_field_names)
        elif isinstance(self.output_field_names, list):
            # Specifically only allowing a list as we'd want the order to remain the same as specified.
            if self.output_field_delimiter is None or (not isinstance(self.output_field_delimiter, str)):
                self.output_field_delimiter = ""
            get_from_value = partial(getattr, value)
            # Added a call to str() in case some fields are not str already as join would complain.
            return self.output_field_delimiter.join(map(str, map(get_from_value, self.output_field_names)))
        return super().to_representation(value)
