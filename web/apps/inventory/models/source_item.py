import json
import logging

from django.contrib.postgres import fields as pg_fields, aggregates as pg_agg
from django.db import models
from django.db.models import expressions, functions


from .. import errors
from ..common import use_type
from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


logger = logging.getLogger(__name__)


# TODO: Need way to edit an order - load existing items into form and make the save intelligent to distinguish.
# TODO: Add 'are you sure' page with summary of order changes.
def add_filter(qs, kwarg_name, value):
    kwarg_names = {
        'single': {
            'str': f"{kwarg_name}__iexact",
            'uuid': kwarg_name,
            'other': kwarg_name,
        },
        'list': f"{kwarg_name}__in",
    }
    new_value = sc_utils.reduce_list(value)
    if isinstance(new_value, list):
        value_type = 'list'
    elif sc_utils.is_valid_uuid(new_value):
        value_type = 'uuid'
    elif isinstance(new_value, str):
        value_type = 'str'
    else:
        value_type = 'other'
    if new_value:
        if isinstance(new_value, list):
            qs = qs.filter(**{kwarg_names['list']: new_value})
        else:
            qs = qs.filter(**{kwarg_names['single'][value_type]: new_value})
    return qs


class SourceItemManager(sc_models.AutocompleteFilterManagerMixin, sc_models.WideFilterManagerMixin, models.Manager):
    def get_queryset(self):
        # return super().get_queryset()  # .exclude(delivered_quantity=0)
        return super().get_queryset().select_related("source")

    def _value_order_distinct(self, field_names, exclude_blank=True):
        if isinstance(field_names, str):
            field_names = [field_names]
        qs = self
        if exclude_blank:
            # This excludes when any one of the field_names is blank.
            q = models.Q()
            for fn in field_names:
                q |= models.Q(**{fn: ""})
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
        return self.values('source_category').order_by('source_category').distinct('source_category')

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

    def override_use_types(self):
        # Importing here to avoid circular dependencies.
        # TODO: if user customizes some, this would clobber those changes.
        from inventory.models import UseTypeOverride
        for uto in UseTypeOverride.objects.all():
            SourceItem.objects.filter(uto.source_item_filter()).update(use_type=uto.use_type)

    def apply_remaining_quantities(self):
        items_to_update = []
        for si in self.filter(remaining_quantity__isnull=True):
            si.remaining_quantity = si.initial_quantity()
            items_to_update.append(si)
        if items_to_update:
            self.bulk_update(items_to_update, ['remaining_quantity'])

    def price_history(self, initial_qs=None):
        if initial_qs is None:
            qs = self
        elif isinstance(initial_qs, models.Q):
            qs = self.filter(initial_qs)
        elif isinstance(initial_qs, models.QuerySet):
            qs = initial_qs
        else:
            raise TypeError(f"initial_qs should be Q or QuerySet.  Got {type(initial_qs)}")

        # Ignore orders where the item wasn't delivered.
        qs = qs.exclude(models.Q(delivered_quantity__lte=0) | models.Q(extended_cost__lte=0))
        # Reset any existing sorting
        qs = qs.order_by().order_by('delivered_date', 'source_id', 'order_number', 'line_item_number')
        # Output is in parallel arrays - used by some graphing libraries.
        data = {
            'item_names': set(),  # distinct set of name/unit size for all items returned.
            'item_name': [],
            'unit_size': [],
            'delivered_date': [],
            'per_use_cost': [],
            'initial_quantity': [],
            'pack_cost': [],
            'source': [],
        }
        for si in qs:
            data['item_names'].add(f"{si.verbose_name or si.cryptic_name} {si.unit_size}")
            data['delivered_date'].append(si.delivered_date)
            # per_use_cost: will give a price per egg - useful for comparing different unit sizes
            data['per_use_cost'].append(si.per_use_cost())
            # initial_quantity: items in a single pack
            data['initial_quantity'].append(si.initial_quantity() / si.delivered_quantity)
            data['item_name'].append(si.verbose_name or si.cryptic_name)
            data['unit_size'].append(si.unit_size)
            # Cannot use pack_cost directly as items using total_weight put the per lb price there.
            data['pack_cost'].append(si.extended_cost / si.delivered_quantity)
            data['source'].append(si.source.name)
        data['item_names'] = ", ".join(data['item_names'])
        return data

    def order_category_totals(
            self, source_id=None, source_name=None, delivered_date=None, order_number=None, general_search=None):
        qs = self.order_items(
            source_id=source_id, source_name=source_name, delivered_date=delivered_date, order_number=order_number,
            general_search=general_search)
        qs = qs.annotate(
            order_category_id=functions.Concat(
                models.F('delivered_date'), models.Value('|'), models.F('source'), models.Value('|'),
                models.F('order_number'), models.F('source_category'), output_field=models.CharField())
        )
        qs = qs.values('source', 'source__name', 'delivered_date', 'order_number', 'order_category_id', 'source_category')
        return qs.annotate(
            sum_extended_cost=models.Sum('extended_cost'),
            count_line_item=models.Count('id'),
            min_line_item_number=models.Min('line_item_number'),
        ).order_by('-delivered_date', 'source__name', 'order_number', 'min_line_item_number')

    def order_list(self, source_id=None, source_name=None, delivered_date=None, order_number=None, general_search=None):
        source_id = sc_utils.reduce_list(source_id)
        source_name = sc_utils.reduce_list(source_name)
        delivered_date = sc_utils.reduce_list(delivered_date)
        order_number = sc_utils.reduce_list(order_number)
        general_search = sc_utils.reduce_list(general_search)
        logger.debug(f"SourceItemManager.order_list: args = {source_id!r}, {source_name!r}, {delivered_date!r}, {order_number!r}")
        if (source_id == "last") or (source_name == "last") or (delivered_date == "last") or (order_number == "last"):
            _order_number = self.order_by('-created').first().order_number
            qs = add_filter(self, "order_number", _order_number)
            logger.debug(f"SourceItemManager.order_list: _order_number = '{_order_number}'")
        else:
            qs = add_filter(self, "source_id", source_id)
            qs = add_filter(qs, "source__name", source_name)
            qs = add_filter(qs, "delivered_date", delivered_date)
            qs = add_filter(qs, "order_number", order_number)
            if general_search:
                qs = qs.filter(self.model.get_wide_filter(general_search, "general"))
        qs = qs.annotate(
            order_id=functions.Concat(
                models.F('delivered_date'), models.Value('|'), models.F('source'), models.Value('|'),
                models.F('order_number'), output_field=models.CharField())
        )
        return qs.values('source', 'source__name', 'delivered_date', 'order_number', 'order_id').annotate(
            sum_extended_cost=models.Sum('extended_cost'),
            count_line_item=models.Count('id'),
            sum_delivered_quantity=models.Sum('delivered_quantity'),
            scanned_filenames=pg_agg.ArrayAgg(models.F('scanned_filename'), distinct=True, ordering=models.F('scanned_filename')),
        ).order_by('-delivered_date', 'source__name', 'order_number')

    def order_items(
            self, source_id=None, source_name=None, delivered_date=None, order_number=None, general_search=None):
        qs = self
        if source_id:
            qs = qs.filter(source_id=source_id)
        if source_name:
            qs = qs.filter(source__name__iexact=source_name)
        if delivered_date:
            qs = qs.filter(delivered_date=delivered_date)
        if order_number:
            qs = qs.filter(order_number=order_number)
        if general_search:
            qs = qs & self.model.get_wide_filter(general_search, "general")
        return qs.order_by('-delivered_date', 'source__name', 'order_number', 'line_item_number')

    def ordered_quantities(self, initial_qs=None):
        if isinstance(initial_qs, models.Q):
            qs = self.filter(initial_qs)
        else:
            qs = (initial_qs or self)
        qs = qs.values('cryptic_name', 'unit_quantity', 'unit_size').annotate(
            delivered_quantities=pg_agg.ArrayAgg('delivered_quantity', distinct=True, ordering=['delivered_quantity']),
            pack_quantities=pg_agg.ArrayAgg('pack_quantity', distinct=True, ordering=['pack_quantity'])).order_by(
            'cryptic_name', 'unit_quantity', 'unit_size')
        return qs


class SourceItem(sc_models.AutocompleteFilterModelMixin, sc_models.WideFilterModelMixin, sc_models.DatedModel):
    wide_filter_fields = {
        'item_id': ['id'],
        'general': [
            'cryptic_name', 'verbose_name', 'common_name', 'item_code', 'extra_notes', 'extra_code', 'unit_size',
            'order_number'],
        'source': ['source__name', 'source_id'],
        'category': ['source_category'],
        'quantity': ['delivered_quantity', 'pack_quantity', 'unit_quantity'],
        'unit_size': ['unit_size'],
        'name': ['cryptic_name', 'verbose_name', 'common_name'],
        'comment': ['extra_notes'],
        'order_number': ['order_number'],
        'item_code': ['item_code', 'extra_code'],
    }
    wide_filter_fields_any = ['source']
    autocomplete_filter_fields = [
        'cryptic_name', 'verbose_name', 'common_name', 'item_code', 'extra_notes', 'extra_code', 'unit_size',
        'order_number',
    ]
    autocomplete_extra_data_fields = {
        'source': 'source_id',
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
    # from django.contrib.postgres import forms as pg_forms
    # pg_forms.SimpleArrayField

    # Peanut Butter.  No brand, unit size, item code, source, location, etc.
    common_name = sc_fields.CharField(help_text="Common brand-less name of item")

    extra_notes = sc_fields.CharField(help_text="Any extra stuff for the item")
    extra_code = sc_fields.CharField(help_text="A second code or whatever.")
    scanned_filename = sc_fields.CharField(help_text="name of the scanned image file in case we need to verify data")

    adjusted_pack_quantity = models.IntegerField(default=1)
    adjusted_count = models.IntegerField(default=1)
    adjusted_pack_cost = sc_fields.MoneyField(default=0)
    adjusted_per_weight_cost = sc_fields.MoneyField(default=0)
    adjusted_weight = sc_fields.DecimalField(default=0)
    adjusted_weight_unit = sc_fields.CharField(default="")
    # TODO: tax, category

    discrepancy = sc_fields.MoneyField(
        help_text="to hold the difference between extended_cost and calculating from quantity/pack_cost")

    use_type = models.CharField(max_length=2, choices=use_type.USE_TYPE_CHOICES, default=use_type.BY_UNIT)
    remaining_quantity = models.IntegerField(null=False, default=0)
    #
    remaining_pack_quantity = models.IntegerField(null=False, default=0)
    remaining_count_quantity = models.IntegerField(null=False, default=0)

    objects = SourceItemManager()

    class Meta:
        ordering = ['-delivered_date', 'source_id', 'order_number', 'line_item_number']

    def __str__(self):
        return f"dl:{self.delivered_date} / cr:{self.created:%Y-%m-%d} / {self.verbose_name or self.cryptic_name}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__iexact", "cryptic_name__icontains", "verbose_name__icontains", "common_name__icontains"

    def debug_str(self):
        # Just a shortcut to display arbitrary fields for debugging
        return f"{self.delivered_date} / {self.cryptic_name} / {self.verbose_name} / {self.unit_size}"

    def get_remaining_quantity(self, _use_type):
        return getattr(self, f"remaining_{use_type.use_type_to_single_word(_use_type)}_quantity")

    def adjust_quantity_x(self, _use_type, expected_remaining_quantity, value):
        pass

    def adjust_quantity(self, _use_type, expected_remaining_quantity, value):
        if self.use_type != _use_type:
            raise errors.UseTypeMismatchError(
                use_type.use_type_to_str(_use_type), use_type.use_type_to_str(self.use_type))
        if self.remaining_quantity < value:
            # raise ValueError(f"Insufficient quantity({self.remaining_quantity}) to satisfy adjustment({value}).")
            raise errors.InsufficientQuantityError(self.remaining_quantity, value)
        if self.remaining_quantity != expected_remaining_quantity:
            raise ValueError(
                f"Expected remaining quantity({expected_remaining_quantity}) does not match "
                f"existing({self.remaining_quantity}).")
        log_data = {
            'id': self.id,
            'previous': self.remaining_quantity,
            'use_type': self.use_type,
            'adjustment': value,
        }
        self.remaining_quantity -= value
        self.save()
        log_data['new'] = self.remaining_quantity
        logger.info(f"adjust_quantity|{json.dumps(log_data, sort_keys=True, default=str)}")
        return self.remaining_quantity

    def calculated_pack_cost(self, round_places=-1):
        """
        :param round_places: If negative, do not round.  If 0 or positive, round to specified places.
        :return:
        """
        unrounded_pack_cost = self.extended_cost / self.delivered_quantity
        if round_places < 0:
            return unrounded_pack_cost
        return round(unrounded_pack_cost, round_places)

    @property
    def name(self):
        """
        returns the name of the item preferring the more human-readable one and falling back to whatever garbage is on
        the invoice/receipt.
        :return:
        """
        return self.common_name or self.verbose_name or self.cryptic_name

    def use_by_count(self):
        return self.use_type == use_type.BY_COUNT

    def use_by_pack(self):
        return self.use_type == use_type.BY_PACK

    def use_by_unit(self):
        return self.use_type == use_type.BY_UNIT

    def initial_quantity(self):
        if self.use_by_pack():
            return self.delivered_quantity
        if self.use_by_unit():
            return self.delivered_quantity * self.pack_quantity
        if self.use_by_count():
            return self.delivered_quantity * self.pack_quantity * self.unit_quantity

    def per_pound_cost(self, rounded_places=-1):
        if self.delivered_quantity == 0:
            return 0
        if self.unit_size.endswith(("lb", "#")):
            # some items use pack_cost as a per pound cost.  For those, we could use that number blindly.
            # or, we could ignore the given pack_cost and calculate it so no conditional logic need done.
            pack_cost = self.extended_cost / self.delivered_quantity
            pack_cost / self.pack_quantity

    def per_use_cost(self, round_places=-1):
        """
        :param round_places: If negative, do not round.  If 0 or positive, round to specified places.
        :return:
        """
        if self.initial_quantity() == 0:
            return 0
        unrounded_per_use_cost = self.extended_cost / self.initial_quantity()
        if round_places < 0:
            return unrounded_per_use_cost
        return round(unrounded_per_use_cost, round_places)

    def related_label(self):
        # Used by grappelli autocomplete
        return f"related_label = {self}"

    def remaining_cost(self):
        return self.per_use_cost() * self.remaining_quantity

    @property
    def source_name(self):
        """
        Shortcut to get name from the source preferring the one without horribly abbreviated terms.
        """
        return self.verbose_name or self.cryptic_name
