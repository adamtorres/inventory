from scrap import models as sc_models
from scrap.models import fields as sc_fields


class Category(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False)

    class Meta:
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name
