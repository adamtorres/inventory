from django.apps import apps
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.shortcuts import render

from grappelli import forms as g_forms

from .models import (
    IncomingItem, IncomingItemGroup, IncomingItemGroupDetail, Item, Source, SourceIncomingDetailTemplate)


@admin.action(description="Add the source-specific details to the incoming group.")
def add_details(model_admin, request, queryset):
    for ig in queryset:
        ig.add_details()


@admin.action(description='Convert incoming group to an inventory change.')
def make_change(model_admin, request, queryset):
    change = apps.get_model('inventory', 'Change')
    # Exclude any IIGs which are already associated with a Change object.
    queryset = queryset.exclude(change__in=queryset.values_list('id', flat=True))
    for ig in queryset:
        c = change.objects.create(source=ig)
        for ii in ig.items.exclude(item__do_not_inventory=True):
            c.items.create(source_item=ii, change_quantity=ii.quantity)


class IncomingItemInline(admin.TabularInline):
    model = IncomingItem
    ordering = ['item__name', ]
    extra = 1


class IncomingItemGroupDetailInline(g_forms.GrappelliSortableHiddenMixin, admin.TabularInline):
    model = IncomingItemGroupDetail
    sortable_field_name = "position"
    extra = 1


class SourceIncomingDetailTemplateInline(g_forms.GrappelliSortableHiddenMixin, admin.TabularInline):
    model = SourceIncomingDetailTemplate
    sortable_field_name = "position"
    extra = 1


class IncomingItemGroupAdmin(admin.ModelAdmin):
    inlines = [IncomingItemGroupDetailInline, IncomingItemInline, ]
    # ordering = ['name', ]
    actions = [add_details, make_change, ]


class SourceAdmin(admin.ModelAdmin):
    inlines = [SourceIncomingDetailTemplateInline, ]
    ordering = ['name', ]


# admin.site.register(IncomingItem)
admin.site.register(IncomingItemGroup, IncomingItemGroupAdmin)
admin.site.register(Item)
admin.site.register(Source, SourceAdmin)
