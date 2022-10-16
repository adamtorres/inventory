from django.db import models
from django.db.models import functions, expressions

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class MeasureManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def avg_report(self):
        qs = self.annotate(item_name=functions.Lower(models.Case(
            models.When(~models.Q(common_name=''), models.F('common_name')),
            models.When(~models.Q(verbose_name=''), models.F('verbose_name')),
            default=models.F('cryptic_name')
        ))).values('item_name', 'converted_unit').annotate(
            min=models.Min('avg_converted_per_measuring'),
            max=models.Max('avg_converted_per_measuring'),
            avg=models.Avg('avg_converted_per_measuring'),
            count=models.Count('id'),
            first_date=models.Min('measure_date'),
            last_date=models.Max('measure_date'),
        )
        qs = qs.order_by('item_name', 'converted_unit')
        return qs


class Measure(sc_models.DatedModel):
    item = models.ForeignKey("inventory.SourceItem", on_delete=models.DO_NOTHING, null=True)

    # Copied from item in case it gets deleted.
    cryptic_name = sc_fields.CharField(blank=False, help_text="Source-specific name of item as it appears on invoices")
    verbose_name = sc_fields.CharField(help_text="More human-readable name of the item")
    common_name = sc_fields.CharField(help_text="Common brand-less name of item")
    item_code = sc_fields.CharField(help_text="String of text that should uniquely identify the item")

    measure_date = models.DateField(help_text="When the measurement was taken")
    measuring_unit = sc_fields.CharField(help_text="Usually some volume unit like cups or gallons")
    measuring_count = models.DecimalField(
        max_digits=9, decimal_places=4, help_text="How many of measuring_unit will be used")
    converted_unit = sc_fields.CharField(help_text="Usually grams")
    converted_amount = models.DecimalField(
        max_digits=9, decimal_places=4, help_text="How much of converted unit did the measuring produce")

    avg_converted_per_measuring = models.DecimalField(
        max_digits=9, decimal_places=4, help_text="Value to use when manually converting")

    objects = MeasureManager()

    class Meta:
        ordering = ('-measure_date', '-modified')

    def __str__(self):
        item_name = self.common_name or self.verbose_name or self.cryptic_name
        return f"{item_name} as {self.converted_unit}"
