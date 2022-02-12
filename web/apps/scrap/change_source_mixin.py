from django.apps import apps
from django.db import models
from django.utils import timezone


class ChangeSourceMixin(models.Model):
    converted_datetime = models.DateTimeField(null=True, blank=True)

    flip_quantity = False

    class Meta:
        abstract = True

    def convert_to_change(self):
        if self.is_converted:
            # Already converted.  Don't try again.
            return
        c = apps.get_model('inventory', 'Change').objects.create(source=self)
        for ii in self.items.all():
            # Since these are Adjustments or Usages, their .item is already an inventory item.
            change_quantity = ii.quantity * (-1 if self.flip_quantity else 1)
            c.items.create(
                source_item=ii, change_quantity=change_quantity, item=ii.item, unit_cost=ii.item.unit_cost,
                line_item_position=ii.line_item_position
            )
        self.converted_datetime = timezone.now()
        self.save()

    def convert_to_change_from_iig(self):
        if self.is_converted:
            # Already converted.  Don't try again.
            return
        c = apps.get_model('inventory', 'Change').objects.create(source=self)
        for ii in self.items.exclude(item__do_not_inventory=True):
            if ii.get_inventory_quantity() <= 0:
                continue
            c.items.create(
                source_item=ii, change_quantity=ii.get_inventory_quantity(), unit_cost=ii.get_cost_per_unit(),
                line_item_position=ii.line_item_position)
        self.converted_datetime = timezone.now()
        self.save()


    @property
    def is_converted(self):
        return self.converted_datetime is not None
