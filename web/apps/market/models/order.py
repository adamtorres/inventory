from django.db import models
from django.utils import timezone

from scrap import models as sc_models
from scrap.models import fields as sc_fields


def today():
    return timezone.localdate(timezone.now())


class Order(sc_models.UUIDModel):
    date_ordered = models.DateField(default=today)
    date_made = models.DateField(null=True, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    who = sc_fields.CharField()
    sale_price = sc_fields.MoneyField(help_text="sale price for all items in the order")
    material_cost = sc_fields.MoneyField(help_text="cost of materials for all items in the order.")

    def __str__(self):
        return f"{self.date_ordered} : {self.who} : {self.state()}"

    def can_be_made(self):
        return not self.date_made

    def can_be_picked_up(self):
        return not self.pickup_date

    def set_order_made(self):
        if not self.date_made:
            self.date_made = timezone.now()
            self.save()

    def set_order_picked_up(self):
        if not self.pickup_date:
            self.pickup_date = timezone.now()
            self.save()

    def state(self):
        if not self.date_made:
            return "Ordered"
        if not self.pickup_date:
            return "Made"
        return "Completed"
