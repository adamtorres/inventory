from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class Tag(sc_models.UUIDModel):
    name = sc_fields.CharField()

    def __str__(self):
        return self.name
