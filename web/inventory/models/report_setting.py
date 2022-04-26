from django.db import models
from scrap import models as sc_models
from scrap.models import fields as sc_fields


class ReportSetting(sc_models.UUIDModel):
    report_name = sc_fields.CharField(blank=False, help_text="name of the report")
    sort_value = models.IntegerField(default=1)
    key = sc_fields.CharField(blank=False, help_text="identifiable string for the value")
    value = sc_fields.CharField(blank=False)

    class Meta:
        ordering = ['report_name', 'sort_value', 'key', 'value']

    def __str__(self):
        return f"{self.report_name}; {self.sort_value}; {self.key}"
