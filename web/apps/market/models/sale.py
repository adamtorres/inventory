from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields

# TODO: Don't have this hardcoded.
SALE_TYPE_SOLD = 'sold'
SALE_TYPE_TRASH = 'trash'
SALE_TYPE_GIVEAWAY = 'giveaway'
SALE_TYPE_PANTRY = 'pantry'
SALE_TYPE_BINGO = 'bingo'
SALE_TYPE_DISCOUNT = 'discount'
SALE_TYPE_COUPON = 'coupon'
SALE_TYPES = [
    (SALE_TYPE_SOLD, 'Sold'),
    (SALE_TYPE_TRASH, 'Trashed'),
    (SALE_TYPE_GIVEAWAY, 'Gave away'),
    (SALE_TYPE_PANTRY, 'Pantry'),
    (SALE_TYPE_BINGO, 'Bingo'),
    (SALE_TYPE_DISCOUNT, 'Discount'),
    (SALE_TYPE_COUPON, 'Coupon'),
]


class Sale(sc_models.UUIDModel):
    on_sale_item = models.ForeignKey("market.OnSaleItem", on_delete=models.CASCADE)
    type = models.CharField(max_length=25, choices=SALE_TYPES, default=SALE_TYPE_SOLD)
    sale_price = sc_fields.MoneyField(help_text="Should mostly be the asking price but could be discounted.")
    packs_sold = models.IntegerField(default=1)
    date_sold = models.DateField()
    is_eod = models.BooleanField(default=False, help_text="Is this an adjustment for the end of a given day?")
