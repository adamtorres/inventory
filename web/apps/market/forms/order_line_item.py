from django.forms import models

from market import models as mkt_models


OrderLineItemFormset = models.inlineformset_factory(mkt_models.Order, mkt_models.OrderLineItem, fields=(
    'line_item_position', 'item_pack',  'quantity',  'sale_price_per_pack', ))
