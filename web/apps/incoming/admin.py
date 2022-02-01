from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from .models import IncomingItem, IncomingItemGroup, Item, Source


class IncomingItemInline(admin.TabularInline):
    model = IncomingItem
    ordering = ['item__name', ]
    # TODO: need to filter the potential items to the ones in the parent order
    extra = 1


class IncomingItemGroupAdmin(admin.ModelAdmin):
    inlines = [IncomingItemInline, ]
    # ordering = ['name', ]


admin.site.register(IncomingItem)
admin.site.register(IncomingItemGroup, IncomingItemGroupAdmin)
admin.site.register(Item)
admin.site.register(Source)
