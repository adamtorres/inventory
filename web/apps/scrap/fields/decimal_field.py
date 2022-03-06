from django.db import models


class DecimalField(models.DecimalField):
    """
    Decimal field with my most common defaults.
    """
    def __init__(self, *args, **kwargs):
        kwargs["max_digits"] = kwargs.get("max_digits", 10)
        kwargs["decimal_places"] = kwargs.get("decimal_places", 4)
        kwargs["null"] = kwargs.get("null", False)
        kwargs["blank"] = kwargs.get("blank", False)
        kwargs["default"] = kwargs.get("default", 0)
        super().__init__(*args, **kwargs)
