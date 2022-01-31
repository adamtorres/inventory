from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from .models import Change, CommonItem, CommonItemNames, Item, ItemChange


class CommonItemNamesInline(admin.TabularInline):
    model = CommonItemNames
    ordering = ['common_item__name', 'name']
    # TODO: need to filter the potential items to the ones in the parent order
    extra = 1


class CommonItemAdmin(admin.ModelAdmin):
    inlines = [CommonItemNamesInline, ]
    ordering = ['name', ]
    # actions = [ship_order, ]


class CommonItemNamesAdmin(admin.ModelAdmin):
    ordering = ['common_item__name', 'name']


admin.site.register(Change)
admin.site.register(CommonItem, CommonItemAdmin)
admin.site.register(CommonItemNames, CommonItemNamesAdmin)
admin.site.register(Item)
admin.site.register(ItemChange)

