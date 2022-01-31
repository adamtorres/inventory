from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models

import uuid


class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("vendor/donator name", max_length=1024, null=False, blank=False)
    active = models.BooleanField("usable source", default=True, null=False, blank=False)

    def __str__(self):
        return self.name
