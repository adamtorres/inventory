from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from .models import Change, CommonItem, CommonItemOtherName, Item, ItemChange


@admin.action(description='Apply inventory changes.')
def apply_item_changes(model_admin, request, queryset):
    for change in queryset.all():
        for i in change.items.exclude(applied=True):
            i.apply_change()


class CommonItemOtherNameInline(admin.TabularInline):
    model = CommonItemOtherName
    ordering = ['common_item__name', 'name']
    # TODO: need to filter the potential items to the ones in the parent order
    extra = 1


class ItemChangeInline(admin.TabularInline):
    model = ItemChange
    ordering = ['item__common_item__name']
    extra = 1


class ChangeAdmin(admin.ModelAdmin):
    inlines = [ItemChangeInline, ]
    actions = [apply_item_changes, ]


class CommonItemAdmin(admin.ModelAdmin):
    inlines = [CommonItemOtherNameInline, ]
    ordering = ['name', ]


class CommonItemOtherNameAdmin(admin.ModelAdmin):
    ordering = ['common_item__name', 'name']


admin.site.register(Change, ChangeAdmin)
admin.site.register(CommonItem, CommonItemAdmin)
# admin.site.register(CommonItemOtherName, CommonItemOtherNameAdmin)
admin.site.register(Item)
# admin.site.register(ItemChange)

