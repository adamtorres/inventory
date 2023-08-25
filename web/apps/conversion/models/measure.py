from django.db import models, transaction
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
        ))).values('item_name', 'measuring_unit', 'converted_unit').annotate(
            min=models.Min('avg_converted_per_measuring'),
            max=models.Max('avg_converted_per_measuring'),
            avg=models.Avg('avg_converted_per_measuring'),
            count=models.Count('id'),
            first_date=models.Min('measure_date'),
            last_date=models.Max('measure_date'),
        )
        qs = qs.order_by('item_name', 'measuring_unit', 'converted_unit')
        return qs

    def refresh_missing_names(self, dry_run=True):
        verbose_name_qs = self.filter(verbose_name="").exclude(item__verbose_name="")
        common_name_qs = self.filter(common_name="").exclude(item__common_name="")
        if dry_run:
            verbose_name_updated = verbose_name_qs.count()
            common_name_updated = common_name_qs.count()
        else:
            # Added .order_by() for tuning to remove any ordering as it is filtering on id.
            # Cannot just do F('item__verbose_name') as Django ORM doesn't like it and gives the following exception:
            #   django.core.exceptions.FieldError: Joined field references are not permitted in this query
            with transaction.atomic():
                verbose_name_updated = verbose_name_qs.update(
                    verbose_name=models.Subquery(
                        self.filter(pk=models.OuterRef('pk')).order_by().values('item__verbose_name')[:1])
                )
                common_name_updated = common_name_qs.update(
                    common_name=models.Subquery(
                        self.filter(pk=models.OuterRef('pk')).order_by().values('item__common_name')[:1])
                )
                if dry_run:
                    transaction.rollback()
        return verbose_name_updated, common_name_updated


class Measure(sc_models.DatedModel):
    item = models.ForeignKey(
        "inventory.SourceItem", on_delete=models.DO_NOTHING, null=True, related_name="measures",
        related_query_name="measures")

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
