from django.db import models


class CharField(models.CharField):
    """
    Character field with my most common defaults.
    """
    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = kwargs.get("max_length", 1024)
        kwargs["null"] = kwargs.get("null", False)
        kwargs["blank"] = kwargs.get("blank", True)
        kwargs["default"] = kwargs.get("default", "")
        super().__init__(*args, **kwargs)
