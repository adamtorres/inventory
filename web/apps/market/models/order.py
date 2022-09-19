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

    class Meta:
        ordering = ['-date_ordered', 'who', 'id']

    def __str__(self):
        return f"{self.date_ordered} : {self.who} : {self.state()}"

    def calculate_totals(self):
        material_cost = 0
        sale_price = 0
        for line_item in self.line_items.all():
            line_item.calculate_totals()
            material_cost += line_item.material_cost
            sale_price += line_item.sale_price
        if (self.material_cost != material_cost) or (self.sale_price != sale_price):
            self.material_cost = material_cost
            self.sale_price = sale_price
            self.save()

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
