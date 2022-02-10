from django.db import models

import uuid


class ConfigItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, null=False, blank=False)
    value = models.CharField(max_length=1024, null=False, blank=False)
    description = models.CharField(max_length=1024, null=False, blank=True, default='')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, related_name='children', null=True, blank=True)

    def __str__(self):
        if self.parent:
            return f"{self.parent} - {self.name}"
        return f"{self.name}"
