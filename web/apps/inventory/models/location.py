from django.db import models

import uuid


class LocationManager(models.Manager):
    def get_cost(self):
        """

        Returns:
            Queryset with name and total_cost for each Location.
        """
        qs = self.exclude(name__in=['garbage']).values('name')
        qs = qs.annotate(
            total_items=models.Count('items__common_item__id', distinct=True),
            total_item_units=models.Sum('items__current_quantity'),
            total_cost=models.Sum(models.F('items__unit_cost') * models.F('items__current_quantity')))
        return qs


class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=1024, null=False, blank=False)

    objects = LocationManager()

    def __str__(self):
        return self.name
