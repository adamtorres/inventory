from django.contrib import admin

from . import models as con_models


class MeasureAdmin(admin.ModelAdmin):
    search_fields = ['cryptic_name', 'verbose_name', 'common_name', 'item_code', ]
    # autocomplete_lookup_fields = {
    #     'fk': ['item'],
    # }
    autocomplete_fields = ['item', ]


admin.site.register(con_models.Measure, MeasureAdmin)
