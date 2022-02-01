from django.db import models

import uuid

from .source import Source


class SourceIncomingDetailTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name="detail_templates")
    name = models.CharField(max_length=1024, null=False, blank=False)
    description = models.CharField(max_length=1024, null=False, blank=True)

    # Starts at 1 for each source
    position = models.PositiveSmallIntegerField("Position", null=True)

    class Meta:
        ordering = ['position']


