from django.db import models

import uuid


class Department(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, null=False, blank=False)

    class Meta:
        pass

    def __str__(self):
        return self.name
