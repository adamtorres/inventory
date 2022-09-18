from django.contrib import admin

from . import models as inv_models


admin.AdminSite.site_header = "Customized Admin Site Header From Inventory"


admin.site.register(inv_models.CommonName)
admin.site.register(inv_models.Source)
admin.site.register(inv_models.SourceItem)
admin.site.register(inv_models.UseTypeOverride)
