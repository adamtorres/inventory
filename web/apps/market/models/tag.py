from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class Tag(sc_models.UUIDModel):
    name = sc_fields.CharField()
    item = models.ForeignKey("market.Item", on_delete=models.CASCADE, related_name="tags", related_query_name="tags")

    def __str__(self):
        return self.name
