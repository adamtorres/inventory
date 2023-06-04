import decimal
from django.db import models
from django.utils import timezone

from scrap import models as sc_models
from scrap.models import fields as sc_fields


def today():
    return timezone.localdate(timezone.now())


def now():
    return timezone.localtime(timezone.now())


class OrderManager(models.Manager):
    def incomplete(self):
        return self.exclude(pickup_date__isnull=False, date_paid__isnull=False)


class Order(sc_models.UUIDModel):
    date_ordered = models.DateField(default=today)
    time_ordered = models.TimeField(default=now)
    date_made = models.DateField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    date_paid = models.DateField(null=True, blank=True)
    who = sc_fields.CharField()
    sale_price = sc_fields.MoneyField(help_text="sale price for all items in the order")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for all items in the order.")

    objects = OrderManager()

    class Meta:
        ordering = ['-date_ordered', '-time_ordered', 'who', 'id']

    def __str__(self):
        return f"{self.date_ordered} : {self.who} : {self.state()}"

    def calculate_totals(self):
        material_cost = 0
        sale_price = 0
        for line_item in self.line_items.all():
            line_item.calculate_totals()
            material_cost += decimal.Decimal(line_item.material_cost)
            sale_price += decimal.Decimal(line_item.sale_price)
        if (self.material_cost != material_cost) or (self.sale_price != sale_price):
            self.material_cost = material_cost
            self.sale_price = sale_price
            self.save()

    def can_be_made(self):
        return not self.date_made

    def can_be_picked_up(self):
        return self.date_made and not self.pickup_date

    def clear_order_made(self):
        if self.date_made:
            self.date_made = None
            self.save()

    def clear_order_paid(self):
        if self.date_paid:
            self.date_paid = None
            self.save()

    def clear_order_picked_up(self):
        if self.pickup_date:
            self.pickup_date = None
            self.save()

    def is_completed(self):
        return self.date_made and self.pickup_date and self.date_paid

    def is_paid(self):
        return bool(self.date_paid)

    def is_picked_up(self):
        return bool(self.pickup_date)

    def set_order_made(self):
        if not self.date_made:
            self.date_made = timezone.now()
            self.save()

    def set_order_paid(self):
        if not self.date_paid:
            self.date_paid = timezone.now()
            self.save()

    def set_order_picked_up(self):
        if not self.pickup_date:
            self.pickup_date = timezone.now()
            self.save()

    def state(self):
        _state = ""
        if not self.date_made:
            _state = "Ordered"
        if not self.pickup_date:
            _state = "Made"
        _state = "Completed"
        return f"{_state}:{'' if self.date_paid else 'NOT'} Paid"
