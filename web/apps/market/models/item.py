from django.db import models
from scrap import models as sc_models
from scrap.models import fields as sc_fields

from market import utils


class Item(sc_models.UUIDModel):
    name = sc_fields.CharField()
    category = models.CharField(max_length=25, choices=utils.ITEM_CATEGORIES, default=utils.ITEM_CATEGORY_COOKIE)
    tags = models.ManyToManyField("market.Tag", related_name="items", related_query_name="items", blank=True)
    material_cost_per_item = sc_fields.MoneyField()

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name
