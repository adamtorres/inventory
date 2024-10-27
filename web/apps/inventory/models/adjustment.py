"""
relation to specific sourceitem and adjusts the remaining pack/count quantity.
Can tie to either inventory recount or usage form.

Spit-balling ideas here.  Will split into separate model files when settled on an implementation.

Maybe: https://django-polymorphic.readthedocs.org/en/latest/
Anti GFK https://github.com/spookylukey/djangoadmintips/tree/master/generic_foreign_key_tests


Using union to combine querysets
https://simonwillison.net/2018/Mar/25/combined-recent-additions/
"""
import datetime

from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class AdjustmentManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('adjustment_group', 'item')


class Adjustment(sc_models.DatedModel):
    notes = sc_fields.CharField(help_text="Anything special about this adjustment.")
    pack_quantity = models.IntegerField(default=0)
    count_quantity = models.IntegerField(default=0)
    no_change = models.BooleanField(default=True)

    adjustment_date = models.DateField(default=datetime.date.today, help_text="When the adjustment actually took place")

    adjustment_group = models.ForeignKey(
        "inventory.AdjustmentGroup", on_delete=models.CASCADE, related_name="adjustments", related_query_name="adjustments")

    item = models.ForeignKey(
        "inventory.SourceItem", on_delete=models.CASCADE, related_name="adjustments", related_query_name="adjustments",
    )

    objects = AdjustmentManager()

    class Meta:
        ordering = ['adjustment_date', 'created']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.no_change = (self.pack_quantity + self.count_quantity) == 0

    def __str__(self):
        return f"{self.item.common_name}, {'not ' if self.no_change else ''}changed/{self.pack_quantity}/{self.count_quantity}, {self.notes!r}"
