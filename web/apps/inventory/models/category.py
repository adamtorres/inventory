from django.db import models

import uuid


class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, null=False, blank=False)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
