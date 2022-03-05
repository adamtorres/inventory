from django.db import models

from scrap import models as sc_models


class Category(sc_models.UUIDModel):
    name = models.CharField(max_length=1024, null=False, blank=False)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
