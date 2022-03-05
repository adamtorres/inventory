from django.db import models

from scrap import models as sc_models


class Department(sc_models.UUIDModel):
    name = models.CharField(max_length=1024, null=False, blank=False)
    abbreviation = models.CharField(max_length=20, null=False, blank=True, default='')

    class Meta:
        pass

    def __str__(self):
        return self.name
