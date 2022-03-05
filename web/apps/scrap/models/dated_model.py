from django.db import models

from .uuid_model import UUIDModel


class DatedModel(UUIDModel):
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    modified = models.DateTimeField(auto_now=True, null=False, blank=False, editable=False)

    class Meta:
        abstract = True
