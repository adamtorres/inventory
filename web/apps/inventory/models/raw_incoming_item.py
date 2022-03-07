import functools

from django.db import models
from django.db.models import functions

from scrap import models as sc_models, fields as sc_fields
from .raw_state import RawState


class RawIncomingItemManager(models.Manager):
    def get_queryset(self):
        """
        Automatically includes the RawState model in orm queries.  Without it, referencing the state would cause a
        separate query for every record.
        """
        return super().get_queryset().select_related('state', 'state__next_state', 'state__next_error_state')

    def __getattr__(self, item):
        ready_prefix = "ready_to_"
        if isinstance(item, str) and item.startswith(ready_prefix) and item != "ready_to_do_action":
            the_something = item[len(ready_prefix):]
            if the_something in RawState.ACTIONS_TO_STATES:
                return functools.partial(self.ready_to_do_action, the_something)
        raise AttributeError(item)

    def ready_to_do_action(self, action, *args):
        state_name = RawState.action_to_state_name(action)
        return self.filter(state__next_state__name=state_name)

    def reset_all(self):
        self.all().update(state=RawState.objects.get(value=0))

    def make_example_changes(self):
        self.filter(name__icontains="x").update(
            name=functions.Concat(models.Value('  '), models.F('name'), models.Value('  ')))


class RawIncomingItemReportManager(models.Manager):
    def group_by_current_state(self):
        return self.values('state', 'state__name').annotate(count=models.Count('id'))

    def console_group_by_current_state(self):
        for s in self.group_by_current_state().order_by('state'):
            print(f"{s['state']} {s['state__name']} = {s['count']}")


class RawIncomingItem(sc_models.DatedModel):
    """
    This is the line as it would be on a spreadsheet.  All information is included verbatim.  Any individual line item
    within an order should be able to tell you all the order information (duplication, yes).
    """
    # Order info - duplicated for all line items within an order
    source = sc_fields.CharField(help_text="source name")
    department = sc_fields.CharField(help_text="department name")
    order_number = sc_fields.CharField(
        help_text="possibly unique text - some sources repeat or slightly modify this for back-ordered items")
    po_text = sc_fields.CharField(help_text="optional text on the invoice")
    order_comment = sc_fields.CharField(help_text="Anything noteworthy about this order")
    order_date = models.DateField(null=True, blank=True, help_text="When the order was placed.")
    delivery_date = models.DateField(help_text="When did we get the items.  Not when the items were shipped.")
    total_price = sc_fields.MoneyField()
    total_packs = sc_fields.DecimalField()

    # Line item info - specific to this one item within an order.
    line_item_position = models.PositiveSmallIntegerField("Position", null=True)

    category = sc_fields.CharField(blank=False, help_text="meat, dairy, produce, etc.")
    name = sc_fields.CharField(blank=False)
    # better_name = sc_fields.CharField(help_text="Less cryptic item name")

    # Won't have this for OUT items for Sysco orders as the invoice just shows "OUT" for the quantity.
    ordered_quantity = sc_fields.DecimalField()
    # delivered = accepted.  Does not include damaged/rejected items.
    delivered_quantity = sc_fields.DecimalField()

    total_weight = sc_fields.DecimalField()
    pack_quantity = sc_fields.DecimalField()
    pack_price = sc_fields.MoneyField()
    pack_tax = sc_fields.MoneyField()
    extended_price = sc_fields.MoneyField()

    item_comment = sc_fields.CharField(help_text="Anything noteworthy about this item")
    scanned_image_filename = sc_fields.CharField(
        help_text="Filename of the scanned file.  Might have multiple per order.")

    state = models.ForeignKey(
        "inventory.RawState", on_delete=models.CASCADE, related_name="raw_items", related_query_name="raw_items",
        to_field="value", default=0
    )
    failure_reasons = models.TextField(null=True, blank=True)

    objects = RawIncomingItemManager()
    reports = RawIncomingItemReportManager()
    non_input_fields = ['state', 'failure_reasons', 'created', 'modified', 'id']

    class Meta:
        ordering = ("delivery_date", "source", "line_item_position")

    def __str__(self):
        return f"{self.delivery_date}|{self.source}|{self.order_number}|{self.line_item_position}|{self.created}"
