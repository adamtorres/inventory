import datetime

from django.db import models
from django.db.models import functions

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class AdjustmentType(models.TextChoices):
    # Nifty feature.  Can provide a custom label by adding `, "Label Text"` after these.
    # Niftier feature.  If the label text is the same as the enum, TextChoices will use that with title case.
    DISCARD = "discard"
    ORDER = "order"
    RECOUNT = "recount"
    SALE = "sale"
    UNKNOWN = 'unknown'
    USAGE = "usage"


class AdjustmentGroupManager(models.Manager):
    def get_queryset(self):
        from . import Adjustment
        return super().get_queryset().prefetch_related(
            models.Prefetch('adjustments', queryset=Adjustment.objects.prefetch_for_group()))

    def get_discards(self):
        return self.filter(adjustment_type=AdjustmentType.DISCARD)

    def get_groups(self, adjustment_type=None, include_closed=False):
        qs = self.all()
        if not include_closed:
            qs = qs.filter(open=True)
        if adjustment_type:
            qs = qs.filter(adjustment_type=adjustment_type)
        return qs

    def get_or_create_open_group(self, adjustment_type=None, start_date=None, end_date=None):
        """
        Find an AdjustmentGroup of the specified type or create it if it doesn't exist.
        If no adjustment_type is specified, it will find the most recent AdjustmentGroup.

        Returns:
            Most recent open AdjustmentGroup or None if no open AdjustmentGroup was found.
        """
        obj = self.open_group(adjustment_type=adjustment_type)
        if not obj:
            adjustment_type = adjustment_type or AdjustmentType.UNKNOWN
            return self.create(adjustment_type=adjustment_type, start_date=start_date, end_date=end_date)
        return obj

    def get_orders(self):
        return self.filter(adjustment_type=AdjustmentType.ORDER)

    def get_recounts(self):
        return self.filter(adjustment_type=AdjustmentType.UNKNOWN)

    def get_sales(self):
        return self.filter(adjustment_type=AdjustmentType.SALE)

    def get_unknowns(self):
        return self.filter(adjustment_type=AdjustmentType.UNKNOWN)

    def get_usages(self):
        return self.filter(adjustment_type=AdjustmentType.USAGE)

    def open_group(self, adjustment_type=None):
        return self.get_groups(adjustment_type=adjustment_type).last()


class AdjustmentGroup(sc_models.DatedModel):
    notes = sc_fields.CharField(help_text="Anything special about this usage group as a whole.")
    start_date = models.DateField(help_text="The start date of the usage group.")
    end_date = models.DateField(help_text="The end date of the usage group.")
    open = models.BooleanField(default=True, help_text="Whether the usage group is actively being added to.")
    adjustment_type = models.CharField(
        max_length=20,
        choices=AdjustmentType.choices,
        default=AdjustmentType.UNKNOWN,
    )

    objects = AdjustmentGroupManager()

    class Meta:
        ordering = ['created', 'start_date']

    def __str__(self):
        return (
            f"AdjustmentGroup({self.adjustment_type}, {'open' if self.open else 'closed'}, "
            f"{self.start_date}, {self.end_date})")

    def calculate_costs(self):
        return self.adjustments.all().aggregate(
            group_pack_cost=functions.Round(models.Sum('pack_cost'), precision=4),
            group_count_cost=functions.Round(models.Sum('count_cost'), precision=4),
            group_total_cost=(
                functions.Round(
                    models.Sum('pack_cost', output_field=models.FloatField())
                    + models.Sum('count_cost', output_field=models.FloatField()),
                    precision=4
                )),
        )
