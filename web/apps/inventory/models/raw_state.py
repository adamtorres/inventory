from django.db import models

from scrap import fields as sc_fields, models as sc_models


class RawState(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False, help_text="short name of the status")
    description = sc_fields.CharField(help_text="Short description of the status")
    value = models.IntegerField(null=False, blank=False, help_text="incrementing value to help sort progress")
