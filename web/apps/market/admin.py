from django.contrib import admin

from . import models as mkt_models


admin.site.register(mkt_models.Item)
admin.site.register(mkt_models.ItemPack)
admin.site.register(mkt_models.OnSaleItemPack)
admin.site.register(mkt_models.Sale)
admin.site.register(mkt_models.Order)
