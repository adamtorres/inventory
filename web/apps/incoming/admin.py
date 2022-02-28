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
    # TODO: work out how to break this up so ChangeSourceMixin is involved.
    change = apps.get_model('inventory', 'Change')
    # Exclude any IIGs which are already associated with a Change object.
    queryset = queryset.exclude(change__in=queryset.values_list('id', flat=True))
    for ig in queryset:
        ig.convert_to_change_from_iig()


# TODO: filter items based on the selected source.
# class OrderForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super(OrderForm, self).__init__(*args, **kwargs)
#         self.fields['parent_order'].queryset = Order.objects.filter(
#             child_orders__ordernumber__exact=self.instance.pk)
#
# class OrderAdmin(admin.ModelAdmin):
#     form = OrderForm
#  It will not work if your admin model have autocomplete_fields attribute in admin model


class IncomingItemInline(admin.TabularInline):
    model = IncomingItem
    extra = 0
    autocomplete_fields = ['item', ]
    readonly_fields = ('extended_price', )
    sortable_field_name = "line_item_position"


class IncomingItemGroupDetailInline(g_forms.GrappelliSortableHiddenMixin, admin.TabularInline):
    model = IncomingItemGroupDetail
    sortable_field_name = "position"
    extra = 0


class SourceIncomingDetailTemplateInline(g_forms.GrappelliSortableHiddenMixin, admin.TabularInline):
    model = SourceIncomingDetailTemplate
    sortable_field_name = "position"
    extra = 1


class IncomingItemGroupAdmin(admin.ModelAdmin):
    inlines = [IncomingItemGroupDetailInline, IncomingItemInline, ]
    ordering = ['-action_date', ]
    actions = [add_details, make_change, ]
    search_fields = ['source__name', 'descriptor', 'comment', 'action_date', 'items__item__name']


class ItemAdmin(admin.ModelAdmin):
    autocomplete_fields = ['common_item']
    search_fields = ['name', 'better_name', 'common_item__name', 'common_item__other_names__name']


class SourceAdmin(admin.ModelAdmin):
    inlines = [SourceIncomingDetailTemplateInline, ]
    ordering = ['name', ]


# admin.site.register(IncomingItem)
admin.site.register(IncomingItemGroup, IncomingItemGroupAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(Source, SourceAdmin)
