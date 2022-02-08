from django.apps import apps
from django.db import models
from django.utils import timezone


class ChangeSourceMixin(models.Model):
    converted_datetime = models.DateTimeField(null=True, blank=True)

    flip_quantity = False

    class Meta:
        abstract = True

    def convert_to_change(self):
        change = apps.get_model('inventory', 'Change')
        c = change.objects.create(source=self)
        for ii in self.items.all():
            # Since these are Adjustments or Usages, their .item is already an inventory item.
            change_quantity = ii.quantity * (-1 if self.flip_quantity else 1)
            c.items.create(
                source_item=ii, change_quantity=change_quantity, item=ii.item, unit_cost=ii.item.unit_cost,
                line_item_position=ii.line_item_position
            )
        self.converted_datetime = timezone.now()
        self.save()

    @property
    def is_converted(self):
        return self.converted_datetime is not None
