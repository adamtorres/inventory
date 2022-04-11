from django.db import models

from .uuid_model import UUIDModel


class DatedModelManagerMixin:
    def recently_created(self, limit=10):
        return self.order_by('-created')[:10]

    def recently_modified(self, limit=10):
        return self.order_by('-modified')[:10]


class DatedModel(UUIDModel):
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    modified = models.DateTimeField(auto_now=True, null=False, blank=False, editable=False)

    class Meta:
        abstract = True
