from django.db import models

import uuid


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, null=False, blank=False)

    def __str__(self):
        return self.name
