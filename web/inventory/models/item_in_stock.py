from dateutil import relativedelta as reldel
import json

from django.utils import timezone
from django.contrib.postgres import aggregates as pg_agg
from django.db import models
from django.db.models import functions

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class ItemInStockManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'raw_incoming_item', 'raw_incoming_item__rawitem_obj', 'raw_incoming_item__rawitem_obj__source',
            'raw_incoming_item__rawitem_obj__category',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name'
        )
        return qs

    def in_stock(self):
        return self.exclude(remaining_unit_quantity__lte=0, remaining_count_quantity__lte=0)


class ItemInStockReportManager(models.Manager):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.select_related(
            'raw_incoming_item', 'raw_incoming_item__rawitem_obj', 'raw_incoming_item__rawitem_obj__source',
            'raw_incoming_item__rawitem_obj__category',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name'
        )
        return qs

    def console_totals_by_year_month_source(self, pivot=False):
        data = self.totals_by_year_month_source(pivot=pivot)
        print(f"all sources = {data['all_sources_in_order']}")
        for year_month in data['data']:
            print(
                f"{year_month['year']}-{year_month['month']} {year_month['month_name_short']}"
                f" {year_month['month_name_long']}")
            for source in data['all_sources_in_order']:
                print(f"\t{source} - {year_month['sources'][source]}")
            print()

    def min_max(self, qs=None):
        if not qs:
            func = getattr(self, 'aggregate')
        else:
            func = getattr(qs, 'annotate')
        return func(
            order_count=models.Count(
                models.Case(
                    models.When(models.Q(raw_incoming_item__po_text='donation'), then=None),
                    default=functions.Concat(
                        'raw_incoming_item__source', models.Value('|'),
                        'raw_incoming_item__order_number', models.Value('|'),
                        'raw_incoming_item__delivery_date'
                        , output_field=models.CharField()
                    )
                ), distinct=True),
            donation_count=models.Count(
                models.Case(
                    models.When(models.Q(raw_incoming_item__po_text='donation'), then=functions.Concat(
                        'raw_incoming_item__source', models.Value('|'),
                        'raw_incoming_item__order_number', models.Value('|'),
                        'raw_incoming_item__delivery_date'
                        , output_field=models.CharField()
                    )),
                    default=None
                ), distinct=True),
            min_delivery_date=models.Min('raw_incoming_item__delivery_date'),
            max_delivery_date=models.Max('raw_incoming_item__delivery_date'),
            min_extended_price=models.Min(
                models.Case(
                    models.When(models.Q(raw_incoming_item__po_text='donation'), then=None),
                    default=models.F('raw_incoming_item__extended_price')
                )
            ),
            max_extended_price=models.Max(
                models.Case(
                    models.When(models.Q(raw_incoming_item__po_text='donation'), then=None),
                    default=models.F('raw_incoming_item__extended_price')
                )
            ),
            min_order_price=models.Min(
                models.Case(
                    models.When(models.Q(raw_incoming_item__po_text='donation'), then=None),
                    default=models.F('raw_incoming_item__total_price')
                )
            ),
            max_order_price=models.Max(
                models.Case(
                    models.When(models.Q(raw_incoming_item__po_text='donation'), then=None),
                    default=models.F('raw_incoming_item__total_price')
                )
            ),
            sum_extended_price=models.Sum('raw_incoming_item__extended_price'),
            sources=pg_agg.ArrayAgg(
                'raw_incoming_item__source', distinct=True, ordering=['raw_incoming_item__source']),
        )

    def min_max_by_common_item(self):
        return self.min_max(self.values('raw_incoming_item__rawitem_obj__common_item_name_group__name__name'))

    def min_max_overall(self):
        return self.min_max()

    def totals_by_year_month(self):
        qs = self.values('raw_incoming_item__delivery_date__year', 'raw_incoming_item__delivery_date__month')
        qs = self.min_max(qs=qs)
        data = qs.order_by('-raw_incoming_item__delivery_date__year', '-raw_incoming_item__delivery_date__month')
        for year_month in data:
            year_month['year'] = year_month.pop('raw_incoming_item__delivery_date__year')
            year_month['month'] = year_month.pop('raw_incoming_item__delivery_date__month')
        return data

    def totals_by_year_month_source(self, pivot=False):
        def start_year_month(_year_month, _sources):
            return {
                "year": _year_month.year,
                "month": _year_month.month,
                "month_name_long": _year_month.strftime("%B"),
                "month_name_short": _year_month.strftime("%b"),
                "sources": {_source: {"source": _source} for _source in _sources},
            }

        qs = self.values(
            'raw_incoming_item__delivery_date__year', 'raw_incoming_item__delivery_date__month',
            'raw_incoming_item__source')
        qs = self.min_max(qs=qs)
        data = qs.order_by(
            '-raw_incoming_item__delivery_date__year', '-raw_incoming_item__delivery_date__month',
            'raw_incoming_item__source')
        all_sources = set()
        for year_month in data:
            year_month['year'] = year_month.pop('raw_incoming_item__delivery_date__year')
            year_month['month'] = year_month.pop('raw_incoming_item__delivery_date__month')
            year_month['source'] = year_month.pop('raw_incoming_item__source')
            all_sources.add(year_month['source'])
        if not pivot:
            return data
        year_month_hold = None
        new_data = []
        all_sources_in_order = sorted(all_sources)
        current_year_month_data = {}  # source keyed dict
        for month_year_source in data:
            # data is sorted "most recent first" so hold should be <= current.
            source = month_year_source['source']
            year = month_year_source['year']
            month = month_year_source['month']
            year_month = timezone.datetime(year, month, 1)
            if year_month_hold is None:
                # First record
                year_month_hold = year_month
                current_year_month_data = start_year_month(year_month, all_sources_in_order)
            if year_month_hold != year_month:
                # Change month - make sure all sources are represented

                # Finish out unrepresented sources for the year/month
                empty_sources = all_sources.difference(current_year_month_data["sources"].keys())
                for empty_source in empty_sources:
                    current_year_month_data["sources"][empty_source] = {"source": empty_source}

                # Add the completed year/month to new_data
                new_data.append(current_year_month_data)
                current_year_month_data = start_year_month(year_month, all_sources_in_order)

                while (year_month_hold - reldel.relativedelta(months=1)) != year_month:
                    # change is 'skip # month(s)' and not 'next month'.
                    # Probably shouldn't hit this as they have multiple orders per month from multiple sources.
                    year_month_hold -= reldel.relativedelta(months=1)
                    for empty_source in all_sources:
                        current_year_month_data["sources"][empty_source] = {"source": empty_source}
                    # Add the empty year/month to new_data
                    new_data.append(current_year_month_data)
                    current_year_month_data = start_year_month(year_month_hold, all_sources_in_order)

                year_month_hold = year_month
                current_year_month_data = start_year_month(year_month_hold, all_sources_in_order)

            current_year_month_data["sources"][source] = {
                k: v for k, v in month_year_source.items() if k not in ['year', 'month', 'sources']}

        if current_year_month_data:
            # Finish out unrepresented sources for the year/month
            empty_sources = all_sources.difference(current_year_month_data["sources"].keys())
            for empty_source in empty_sources:
                current_year_month_data["sources"][empty_source] = {"source": empty_source}

            # Add the completed year/month to new_data
            new_data.append(current_year_month_data)
        return {"data": new_data, "all_sources_in_order": all_sources_in_order}


class ItemInStock(sc_models.DatedModel):
    raw_incoming_item = models.OneToOneField(
        "inventory.RawIncomingItem", on_delete=models.CASCADE, related_name="in_stock", related_query_name="in_stock")
    original_unit_quantity = sc_fields.DecimalField(help_text="delivered_quantity * pack_quantity")
    remaining_unit_quantity = sc_fields.DecimalField()
    remaining_count_quantity = sc_fields.DecimalField()
    unit_price = sc_fields.MoneyField()
    count_price = sc_fields.MoneyField()

    objects = ItemInStockManager()
    reports = ItemInStockReportManager()

    class Meta:
        ordering = (
            'raw_incoming_item__rawitem_obj__source__name',
            'raw_incoming_item__rawitem_obj__common_item_name_group__name__name', 'raw_incoming_item__delivery_date',
            'raw_incoming_item__created',
        )
