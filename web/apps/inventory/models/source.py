from django.db import models

from scrap import models as sc_models


class SourceManager(models.Manager):
    def active_sources(self):
        return self.exclude(active=False)


class Source(sc_models.DatedModel):
    name = models.CharField(max_length=1024, null=False, blank=False, help_text="vendor/donator name")
    active = models.BooleanField(default=True, null=False, blank=False, help_text="is a usable source")

    objects = SourceManager()

    def __str__(self):
        return self.name

    # def most_recent_order(self):
    #     return self.item_groups.order_by('-action_date')[:1].first()
