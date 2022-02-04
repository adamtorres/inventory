from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from .models import (
    Adjustment, AdjustmentItem, Category, Change, CommonItem, CommonItemOtherName, Item, ItemChange, Location, Usage,
    UsageItem)


@admin.action(description='Apply inventory changes.')
def apply_item_changes(model_admin, request, queryset):
    for change in queryset.all():
        for i in change.items.exclude(applied=True):
            i.apply_change()


@admin.action(description='Convert to an inventory change.')
def make_change(model_admin, request, queryset):
    # Exclude any groups which are already associated with a Change object.
    queryset = queryset.exclude(change__in=queryset.values_list('id', flat=True))
    for ig in queryset:
        c = Change.objects.create(source=ig)
        for ii in ig.items.all():
            c.items.create(source_item=ii, change_quantity=ii.quantity)


class AdjustmentItemInline(admin.TabularInline):
    model = AdjustmentItem
    extra = 1


class CommonItemOtherNameInline(admin.TabularInline):
    model = CommonItemOtherName
    ordering = ['common_item__name', 'name']
    # TODO: need to filter the potential items to the ones in the parent order
    extra = 1


class ItemChangeInline(admin.TabularInline):
    model = ItemChange
    ordering = ['item__common_item__name']
    extra = 1
    autocomplete_lookup_fields = {
        'generic': [['source_item_content_type', 'source_item_object_id']],
    }


class UsageItemInline(admin.TabularInline):
    model = UsageItem
    extra = 1


class AdjustmentAdmin(admin.ModelAdmin):
    inlines = [AdjustmentItemInline, ]
    actions = [make_change, ]


class ChangeAdmin(admin.ModelAdmin):
    inlines = [ItemChangeInline, ]
    actions = [apply_item_changes, ]
    autocomplete_lookup_fields = {
        'generic': [['source_content_type', 'source_object_id']],
    }


class CommonItemAdmin(admin.ModelAdmin):
    inlines = [CommonItemOtherNameInline, ]
    ordering = ['name', ]
    search_fields = ['name', 'other_names__name']


class CommonItemOtherNameAdmin(admin.ModelAdmin):
    ordering = ['common_item__name', 'name']


class ItemAdmin(admin.ModelAdmin):
    autocomplete_fields = ['common_item']
    search_fields = ['common_item__name', 'common_item__other_names__name']


class UsageAdmin(admin.ModelAdmin):
    inlines = [UsageItemInline, ]
    actions = [make_change, ]


admin.site.register(Adjustment, AdjustmentAdmin)
admin.site.register(Category)
admin.site.register(Change, ChangeAdmin)
admin.site.register(CommonItem, CommonItemAdmin)
# admin.site.register(CommonItemOtherName, CommonItemOtherNameAdmin)
admin.site.register(Item, ItemAdmin)
# admin.site.register(ItemChange)
admin.site.register(Location)
admin.site.register(Usage, UsageAdmin)

