from django.db import models
from scrap import models as sc_models
from scrap.models import fields as sc_fields


ITEM_CATEGORY_COOKIE = "cookie"
ITEM_CATEGORY_CAKE = "cake"
ITEM_CATEGORY_BREAD = "bread"
ITEM_CATEGORY_OTHER = "other"
ITEM_CATEGORIES = [
    (ITEM_CATEGORY_BREAD, "Bread"),
    (ITEM_CATEGORY_CAKE, "Cake"),
    (ITEM_CATEGORY_COOKIE, "Cookie"),
    (ITEM_CATEGORY_OTHER, "Other"),
]


class Item(sc_models.UUIDModel):
    name = sc_fields.CharField()
    category = models.CharField(max_length=25, choices=ITEM_CATEGORIES, default=ITEM_CATEGORY_COOKIE)

    def __str__(self):
        return self.name
