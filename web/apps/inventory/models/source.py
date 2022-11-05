from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class SourceManager(models.Manager):
    def active_sources(self):
        return self.exclude(active=False)


class Source(sc_models.UUIDModel):
    # This is where we purchased the item - RSM, Sysco, Broulims, etc.
    name = sc_fields.CharField(blank=False, help_text="vendor/donator name")
    active = models.BooleanField(default=True, null=False, blank=False, help_text="is a usable source")

    objects = SourceManager()

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
