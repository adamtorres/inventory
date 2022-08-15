from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class SourceItemManager(sc_models.WideFilterManagerMixin, models.Manager):
    def common_names(self):
        return self.values('common_name').order_by('common_name').distinct('common_name')

    def cryptic_names(self):
        return self.values('cryptic_name').order_by('cryptic_name').distinct('cryptic_name')

    def order_numbers(self):
        return self.values('order_number').order_by('order_number').distinct('order_number')

    def orders(self):
        qs = self.values('source', 'delivered_date', 'order_number')
        qs = qs.order_by('delivered_date', 'source', 'order_number')
        return qs.distinct('delivered_date', 'source', 'order_number')

    def source_names(self):
        return self.values('source__name').order_by('source__name').distinct('source__name')

    def source_categories(self):
        return self.values('source_category').order_by('source_category').distinct('source_category')

    def unit_sizes(self):
        return self.values('unit_size').order_by('unit_size').distinct('unit_size')

    def verbose_names(self):
        return self.values('verbose_name').order_by('verbose_name').distinct('verbose_name')


class SourceItem(sc_models.WideFilterModelMixin, sc_models.UUIDModel):
    wide_filter_fields = {
        'name': ['cryptic_name', 'verbose_name', 'common_name'],
        'general': ['cryptic_name', 'verbose_name', 'common_name', 'item_code', 'extra_notes', 'extra_code'],
    }

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

    # This doesn't change any of the words or order.
    # Just changes things like "PORK LOIN BNLS CC STR/OFF" to "Pork loin boneless center cut strap off"
    verbose_name = sc_fields.CharField(blank=False, help_text="More human-readable name of the item")

    # This might also change over time.  Yay.
    item_code = sc_fields.CharField(blank=False, help_text="String of text that should uniquely identify the item")

    # 5x 12pk of 12oz soda - this is 5 12pks of soda cans
    #   quantity=5, pack_quantity=12, unit_quantity=12, unit_size=12oz
    # 3x 50lb bag of flour - this is 3 big bags of flour
    #   quantity=3, pack_quantity=1, unit_quantity=50, unit_size=50lb
    # 1x 36pk of 26oz salt - this is a box that has 36 cans of salt
    #   quantity=1, pack_quantity=36, unit_quantity=26, unit_size=26oz

    delivered_quantity = models.IntegerField(
        default=1, help_text="How many packs did we get?  Not ordered or back-ordered; physically present.")

    pack_cost = sc_fields.MoneyField()
    pack_quantity = sc_fields.CharField(blank=False, help_text="For a pack of 6 #10 cans, this would be 6.")

    # unit_cost = sc_fields.MoneyField(help_text="calculated and saved to make other calculations easier")
    unit_quantity = models.IntegerField(
        default=1, help_text="count within a unit - dozen eggs would be 12.  50lb flour would be 50.")

    unit_size = sc_fields.CharField(
        blank=False, help_text="1dz, 50lb, 12pk.  Might have the same number as unit_quantity")

    extended_cost = sc_fields.MoneyField(help_text="includes tax and any shipping fees")

    total_weight = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    individual_weights = pg_fields.ArrayField(models.DecimalField(max_digits=8, decimal_places=4), default=list)

    # Peanut Butter.  No brand, unit size, item code, source, location, etc.
    common_name = sc_fields.CharField(blank=False, help_text="Common brand-less name of item")

    extra_notes = sc_fields.CharField(help_text="Any extra stuff for the item")
    extra_code = sc_fields.CharField(help_text="A second code or whatever.")
    scanned_filename = sc_fields.CharField(help_text="name of the scanned image file in case we need to verify data")

    # TODO: tax, category

    discrepancy = sc_fields.MoneyField(
        help_text="to hold the difference between extended_cost and calculating from quantity/pack_cost")

    objects = SourceItemManager()

    def __str__(self):
        return f"{self.delivered_date} / {self.verbose_name or self.cryptic_name}"
