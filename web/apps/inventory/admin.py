from django.contrib import admin

from . import forms as inv_forms, models as inv_models


admin.AdminSite.site_header = "Customized Admin Site Header From Inventory"


class AdjustmentInline(admin.TabularInline):
    model = inv_models.Adjustment


class AdjustmentGroupAdmin(admin.ModelAdmin):
    inlines = [AdjustmentInline]


class SourceItemAdmin(admin.ModelAdmin):
    form = inv_forms.SourceItemAdminForm
    search_fields = ['cryptic_name', 'verbose_name', 'common_name', 'item_code', 'order_number', ]
    fieldsets = (
        ('Order', {
            'fields': ('delivered_date', 'source', 'customer_number', 'order_number', 'po_text')}),
        ('Item', {
            'fields': (
                'line_item_number', 'source_category', 'item_code', 'extra_code', 'brand', 'cryptic_name',
                'verbose_name', 'common_name', 'pack_quantity', 'unit_quantity', 'unit_size',)}),
        ('Quantity And Cost', {
            'fields': (
                'delivered_quantity', 'total_weight', 'individual_weights', 'pack_cost', 'extended_cost',
                'adjusted_count', 'adjusted_pack_quantity', 'adjusted_weight', 'adjusted_weight_unit',
                'adjusted_per_weight_cost', 'adjusted_pack_cost',
            )}),
        ('Other Garbage', {
            'fields': ('extra_notes', 'scanned_filename', 'discrepancy',)}),
        ('Remaining Quantity', {
            'fields': (
                'use_type', 'remaining_quantity', 'remaining_pack_quantity', 'remaining_count_quantity',)}),
    )


admin.site.register(inv_models.AdjustmentGroup, AdjustmentGroupAdmin)
admin.site.register(inv_models.Adjustment)
admin.site.register(inv_models.CommonName)
admin.site.register(inv_models.SearchCriteria)
admin.site.register(inv_models.Source)
admin.site.register(inv_models.SourceItem, SourceItemAdmin)
admin.site.register(inv_models.UseTypeOverride)
