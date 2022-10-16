from django.contrib import admin

from . import models as inv_models


admin.AdminSite.site_header = "Customized Admin Site Header From Inventory"


class SourceItemAdmin(admin.ModelAdmin):
    search_fields = ['cryptic_name', 'verbose_name', 'common_name', 'item_code', ]


admin.site.register(inv_models.CommonName)
admin.site.register(inv_models.Source)
admin.site.register(inv_models.SourceItem, SourceItemAdmin)
admin.site.register(inv_models.UseTypeOverride)
