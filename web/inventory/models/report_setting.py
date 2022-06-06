from django.contrib.postgres import aggregates as pg_agg
from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class ReportSettingManager(models.Manager):
    def for_report(self, report_name, as_dict=True, single_as_scalar=True, convert_to_number=True):
        qs = self.filter(report_name=report_name).values('key').annotate(
            values=pg_agg.ArrayAgg('value', ordering=['sort_value'])
        )
        if not as_dict:
            return qs
        result = {}
        for data in qs:
            result[data['key']] = data['values']
            if convert_to_number:
                for i in range(len(result[data['key']])):
                    v = result[data['key']][i]
                    try:
                        v = int(result[data['key']][i])
                    except ValueError:
                        try:
                            v = float(result[data['key']][i])
                        except ValueError:
                            pass
                    result[data['key']][i] = v
            if single_as_scalar and len(result[data['key']]) == 1:
                result[data['key']] = result[data['key']][0]
        return result


class ReportSetting(sc_models.UUIDModel):
    report_name = sc_fields.CharField(blank=False, help_text="name of the report")
    sort_value = models.IntegerField(default=1)
    key = sc_fields.CharField(blank=False, help_text="identifiable string for the value")
    value = sc_fields.CharField(blank=False)

    objects = ReportSettingManager()

    class Meta:
        ordering = ['report_name', 'key', 'sort_value', 'value']

    def __str__(self):
        return f"{self.report_name}; {self.key}; {self.sort_value}; {self.value}"
    # User ReportSetting.objects.for_report('item_price_change') to get the values.
    # report_name = 'item_price_change'
    # sort_value = 0, key = 'months', value = '6'
    # sort_value = 0, key = 'items', value = 'flour'
    # sort_value = 1, key = 'items', value = 'ground beef'
    # sort_value = 2, key = 'items', value = 'large eggs'
    # sort_value = 3, key = 'items', value = 'eggs'
    # sort_value = 4, key = 'items', value = 'butter'

    # ReportSetting.objects.for_report('item_price_change')
    # Returns {'items': ['flour', 'butter', 'ground beef', 'large eggs', 'eggs'], 'months': 6}
