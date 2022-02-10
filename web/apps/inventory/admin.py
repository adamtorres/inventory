from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from .models import (
    Adjustment, AdjustmentItem, Category, Change, CommonItem, CommonItemOtherName, ConfigItem, Item, ItemChange,
    Location, Usage, UsageItem)


@admin.action(description='Apply inventory changes.')
def apply_item_changes(model_admin, request, queryset):
    for change in queryset.all():
        change.apply_changes()


@admin.action(description='Convert to an inventory change.')
def convert_to_change(model_admin, request, queryset):
    # Called on Adjustments and Usages.
    # Exclude any groups which are already associated with a Change object.
    # TODO: the item on the change was unpopulated?  Should limit that drop down based on the source item.
    queryset = queryset.exclude(change__in=queryset.values_list('id', flat=True))
    for adj_or_usage in queryset:
        adj_or_usage.convert_to_change()


class AdjustmentItemInline(admin.TabularInline):
    model = AdjustmentItem
    sortable_field_name = "line_item_position"
    extra = 0
    autocomplete_fields = ['item', ]


class CommonItemOtherNameInline(admin.TabularInline):
    model = CommonItemOtherName
    ordering = ['common_item__name', 'name']
    # TODO: need to filter the potential items to the ones in the parent order
    extra = 0


class ConfigItemInline(admin.TabularInline):
    model = ConfigItem
    ordering = ['name', ]
    extra = 0


class ItemChangeInline(admin.TabularInline):
    model = ItemChange
    sortable_field_name = "line_item_position"
    extra = 0
    autocomplete_lookup_fields = {
        'generic': [['source_item_content_type', 'source_item_object_id']],
    }
    readonly_fields = ('applied_datetime', )


class UsageItemInline(admin.TabularInline):
    model = UsageItem
    sortable_field_name = "line_item_position"
    extra = 0
    autocomplete_fields = ['item', ]


class AdjustmentAdmin(admin.ModelAdmin):
    inlines = [AdjustmentItemInline, ]
    actions = [convert_to_change, ]
    readonly_fields = ('converted_datetime', )
    ordering = ['-action_date', ]


class ChangeAdmin(admin.ModelAdmin):
    inlines = [ItemChangeInline, ]
    actions = [apply_item_changes, ]
    autocomplete_lookup_fields = {
        'generic': [['source_content_type', 'source_object_id']],
    }
    readonly_fields = ('applied_datetime', )
    ordering = ['-action_date', ]


class CommonItemAdmin(admin.ModelAdmin):
    inlines = [CommonItemOtherNameInline, ]
    ordering = ['name', ]
    search_fields = ['name', 'other_names__name']


class CommonItemOtherNameAdmin(admin.ModelAdmin):
    ordering = ['common_item__name', 'name']


class ConfigItemAdmin(admin.ModelAdmin):
    inlines = [ConfigItemInline, ]
    ordering = ['parent__name', 'name', ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            id = request.resolver_match.kwargs.get('object_id')
            kwargs["queryset"] = ConfigItem.objects.exclude(id=id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class ItemAdmin(admin.ModelAdmin):
    autocomplete_fields = ['common_item']
    search_fields = ['common_item__name', 'common_item__other_names__name']


class UsageAdmin(admin.ModelAdmin):
    inlines = [UsageItemInline, ]
    actions = [convert_to_change, ]
    readonly_fields = ('converted_datetime', )
    ordering = ['-action_date', ]


admin.site.register(Adjustment, AdjustmentAdmin)
admin.site.register(Category)
admin.site.register(Change, ChangeAdmin)
admin.site.register(CommonItem, CommonItemAdmin)
# admin.site.register(CommonItemOtherName, CommonItemOtherNameAdmin)
admin.site.register(ConfigItem, ConfigItemAdmin)
admin.site.register(Item, ItemAdmin)
# admin.site.register(ItemChange)
admin.site.register(Location)
admin.site.register(Usage, UsageAdmin)

