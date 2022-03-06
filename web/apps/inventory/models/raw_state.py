from django.db import models

from scrap import fields as sc_fields, models as sc_models


class RawStateManager(models.Manager):
    def get_by_natural_key(self, value):
        return self.get(value=value)


class RawState(sc_models.UUIDModel):
    name = sc_fields.CharField(blank=False, help_text="short name of the status")
    description = sc_fields.CharField(help_text="Short description of the status")
    value = models.IntegerField(null=False, blank=False, help_text="incrementing value to help sort progress")

    objects = RawStateManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(name="unique_raw_state_value", fields=('value', ))
        ]
        ordering = ('value', )

    def __str__(self):
        return f"({self.value}) {self.name}"
