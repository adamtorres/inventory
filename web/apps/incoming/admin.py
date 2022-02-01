from django.apps import apps
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from .models import IncomingItem, IncomingItemGroup, Item, Source


@admin.action(description='Convert incoming group to an inventory change.')
def make_change(model_admin, request, queryset):
    change = apps.get_model('inventory', 'Change')
    # Exclude any IIGs which are already associated with a Change object.
    queryset = queryset.exclude(change__in=queryset.values_list('id', flat=True))
    for ig in queryset:
        c = change.objects.create(source=ig)
        for ii in ig.items.all():
            c.items.create(source_item=ii, change_quantity=ii.quantity)


class IncomingItemInline(admin.TabularInline):
    model = IncomingItem
    ordering = ['item__name', ]
    # TODO: need to filter the potential items to the ones in the parent order
    extra = 1


class IncomingItemGroupAdmin(admin.ModelAdmin):
    inlines = [IncomingItemInline, ]
    # ordering = ['name', ]
    actions = [make_change, ]


# admin.site.register(IncomingItem)
admin.site.register(IncomingItemGroup, IncomingItemGroupAdmin)
admin.site.register(Item)
admin.site.register(Source)
