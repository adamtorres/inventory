from django.contrib.postgres import fields as pg_fields
from django.db import models
from django.db.models import expressions, functions


from scrap import models as sc_models
from scrap.models import fields as sc_fields


class SourceItemManager(sc_models.WideFilterManagerMixin, models.Manager):
    def _value_order_distinct(self, field_names, exclude_blank=True):
        if isinstance(field_names, str):
            field_names = [field_names]
        qs = self
        if exclude_blank:
            # This excludes when any one of the field_names is blank.
            q = models.Q()
            for fn in field_names:
                q |= models.Q(**{fn: ""})
            # # This excludes only when all the field_names are blank.
            # q = models.Q(**{fn: "" for fn in field_names})
            qs = qs.exclude(q)
        return qs.values(*field_names).order_by(*field_names).distinct(*field_names)

    def common_names(self):
        return self._value_order_distinct('common_name')

    def cryptic_names(self):
        return self._value_order_distinct('cryptic_name')

    def order_numbers(self):
        return self._value_order_distinct('order_number')

    def orders(self):
        return self._value_order_distinct(['delivered_date', 'source', 'order_number'])

    def source_names(self):
        return self._value_order_distinct('source__name')

    def source_categories(self):
        return self.values('source_category').annotate(
            line_items=models.Count('id'),
            row_number=expressions.Window(
                expression=functions.RowNumber(), order_by=models.F('source_category').asc()),
        ).order_by('source_category')

    def unit_sizes(self):
        return self._value_order_distinct('unit_size')

    def verbose_names(self):
        return self._value_order_distinct('verbose_name')

    def missing_verbose_name(self):
        return self.filter(verbose_name="").values('cryptic_name').order_by('cryptic_name').distinct('cryptic_name')

    def stats(self):
        return self.annotate(
            order_id=functions.Concat(
                models.F('delivered_date'), models.F('source'), models.F('order_number'),
                output_field=models.CharField())
        ).aggregate(
            min_delivered_date=models.Min('delivered_date'),
            max_delivered_date=models.Max('delivered_date'),
            sum_extended_cost=models.Sum('extended_cost'),
            count_line_item=models.Count('id'),
            count_order=models.Count('order_id', distinct=True),
        )


class SourceItem(sc_models.WideFilterModelMixin, sc_models.UUIDModel):
    wide_filter_fields = {
        'item_id': ['id'],
        'general': [
            'cryptic_name', 'verbose_name', 'common_name', 'item_code', 'extra_notes', 'extra_code', 'unit_size',
            'order_number'],
        'source': ['source__name'],
        'category': ['source_category'],
        'quantity': ['delivered_quantity', 'pack_quantity', 'unit_quantity'],
        'unit_size': ['unit_size'],
        'name': ['cryptic_name', 'verbose_name', 'common_name'],
        'comment': ['extra_notes'],
        'order_number': ['order_number'],
    }
    wide_filter_fields_any = []

    delivered_date = models.DateField()
    source = models.ForeignKey("inventory.Source", on_delete=models.CASCADE)
    brand = sc_fields.CharField(verbose_name="Brand name")

    customer_number = sc_fields.CharField()
    order_number = sc_fields.CharField()
    po_text = sc_fields.CharField()

    line_item_number = models.IntegerField(default=0, null=False, blank=True)

    source_category = sc_fields.CharField(
        help_text="Source-specific category.  Need our own as some of these don't make sense.")

    # This might vary from order to order as RSM and Sysco have not been consistent.
    cryptic_name = sc_fields.CharField(blank=False, help_text="Source-specific name of item as it appears on invoices")

    # This doesn't change any of the words or order.  It might add words where completely missing.
    # Just changes things like "PORK LOIN BNLS CC STR/OFF" to "Pork loin boneless center cut strap off"
    verbose_name = sc_fields.CharField(help_text="More human-readable name of the item")

    # This might also change over time.  Yay.
    item_code = sc_fields.CharField(help_text="String of text that should uniquely identify the item")

    # 5x 12pk of 12oz soda - this is 5 12pks of soda cans
    #   quantity=5, pack_quantity=12, unit_quantity=12, unit_size=12oz
    # 3x 50lb bag of flour - this is 3 big bags of flour
    #   quantity=3, pack_quantity=1, unit_quantity=50, unit_size=50lb
    # 1x 36pk of 26oz salt - this is a box that has 36 cans of salt
    #   quantity=1, pack_quantity=36, unit_quantity=26, unit_size=26oz

    delivered_quantity = models.IntegerField(
        default=1, help_text="How many packs did we get?  Not ordered or back-ordered; physically present.")

    pack_cost = sc_fields.MoneyField()
    pack_quantity = models.IntegerField(default=1, help_text="For a pack of 6 #10 cans, this would be 6.")

    # unit_cost = sc_fields.MoneyField(help_text="calculated and saved to make other calculations easier")
    unit_quantity = models.IntegerField(
        default=1, help_text="count within a unit - dozen eggs would be 12.  50lb flour would be 50.")

    unit_size = sc_fields.CharField(help_text="1dz, 50lb, 12pk.  Might have the same number as unit_quantity")

    extended_cost = sc_fields.MoneyField(help_text="includes tax and any shipping fees")

    total_weight = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    individual_weights = pg_fields.ArrayField(models.DecimalField(max_digits=8, decimal_places=4), default=list)

    # Peanut Butter.  No brand, unit size, item code, source, location, etc.
    common_name = sc_fields.CharField(help_text="Common brand-less name of item")

    extra_notes = sc_fields.CharField(help_text="Any extra stuff for the item")
    extra_code = sc_fields.CharField(help_text="A second code or whatever.")
    scanned_filename = sc_fields.CharField(help_text="name of the scanned image file in case we need to verify data")

    # TODO: tax, category

    discrepancy = sc_fields.MoneyField(
        help_text="to hold the difference between extended_cost and calculating from quantity/pack_cost")

    # by_pack would mean each use is (pack_quantity) of (unit_size)
    # by_unit would mean each use is (unit_size)
    # by_count would mean each use is a subdivision of unit_size if available.
    #   Some products have a 'lb' unit_size but would not make sense to break down to that level.
    #   Others, like #10 cans, are a single unit and should not be subdivided.

    # Example:
    # Order 385651775, "labella pasta noodle egg xwide"
    #   delivered_quantity=3, pack_quantity=2, unit_size=5lb, unit_quantity=5
    # by_pack would mean each use is 2(pack_quantity) 5lb(unit_size) units for a total of 10lb of egg noodle.
    # by_unit would mean each use is 1 5lb unit
    # by_count would mean each use is 1lb - would not make sense for this product.

    # Example:
    # Order 485212206, "whlfcls egg shell large white"
    #   delivered_quantity=1, pack_quantity=1, unit_size=30dz, unit_quantity=360
    # by_pack would mean each use is 1(pack_quantity) unit of 30dz(unit_size) eggs
    # by_unit would mean each use is 1 30dz(unit_size) of eggs
    # by_count would mean 1 egg makes sense for this product.

    # Example:
    # Order 485292245, "sys cls bean green cut 4sv bl fcy"
    #   delivered_quantity=3, pack_quantity=6, unit_size=#10, unit_quantity=1
    # by_pack would mean each use is 6(pack_quantity) unit of #10(unit_size) cans
    # by_unit would mean each use is 1 #10(unit_size) of cans
    # by_count would not make sense for this product as a single #10 can cannot be subdivided.
    use_type = "by_count|by_unit|by_pack"

    objects = SourceItemManager()

    def __str__(self):
        return f"{self.delivered_date} / {self.verbose_name or self.cryptic_name}"
