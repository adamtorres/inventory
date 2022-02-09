from django.db import models

import uuid


class SourceManager(models.Manager):
    def active_sources(self):
        return self.exclude(active=False)


class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField("vendor/donator name", max_length=1024, null=False, blank=False)
    active = models.BooleanField("usable source", default=True, null=False, blank=False)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)

    objects = SourceManager()

    def __str__(self):
        return self.name

    def most_recent_order(self):
        return self.item_groups.order_by('-action_date')[:1].first()
