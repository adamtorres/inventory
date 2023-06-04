from django.contrib import admin

from . import models as mkt_models


admin.AdminSite.site_header = "Customized Admin Site Header From Market"


class OrderLineItemInline(admin.TabularInline):
    model = mkt_models.OrderLineItem
    extra = 3


class OrderAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['who', 'sale_price', 'material_cost']}),
        ('Date information', {'fields': ['date_ordered', 'time_ordered', 'date_made', 'pickup_date']}),
    ]
    inlines = [OrderLineItemInline]
    # list_display = ('question_text', 'pub_date', 'was_published_recently')
    # list_filter = ['pub_date']
    # search_fields = ['question_text']


admin.site.register(mkt_models.Item)
admin.site.register(mkt_models.OnSaleItem)
admin.site.register(mkt_models.Order, OrderAdmin)
admin.site.register(mkt_models.Sale)
admin.site.register(mkt_models.Tag)
