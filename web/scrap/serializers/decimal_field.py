from rest_framework import serializers


class DecimalField(serializers.DecimalField):
    def __init__(
            self, max_digits=10, decimal_places=4, coerce_to_string=None, max_value=None, min_value=None,
            localize=False, rounding=None, **kwargs):
        kwargs["default"] = kwargs.get("default", 0)
        kwargs['allow_null'] = kwargs.get('allow_null', False)
        super().__init__(
            max_digits, decimal_places, coerce_to_string=coerce_to_string, max_value=max_value, min_value=min_value,
            localize=localize, rounding=rounding, **kwargs)
