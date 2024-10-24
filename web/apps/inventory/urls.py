from django import urls
from rest_framework import urlpatterns as rf_urls

from . import views as i_views


app_name = "inventory"

# api_chart_urls = [
#     urls.path("api/sourceitem/chartdata/", i_views.APIChartDataView.as_view(), name="api_sourceitem_chartdata"),
# ]
# api_chart_urls = rf_urls.format_suffix_patterns(api_chart_urls, allowed=['api', 'chartjs'])

urlpatterns = [
    urls.path("api/saved_search/<uuid:pk>", i_views.APISavedSearchView.as_view(), name="saved_search"),

    urls.path(
        "api/sourceitem/autocomplete/", i_views.APISourceItemAutocompleteSearchView.as_view(),
        name="api_sourceitem_autocomplete"),

    urls.path(
        "api/sourceitem/chartdata/<str:report_name>/", i_views.APIChartDataView.as_view(),
        name="api_sourceitem_chartdata"),

    urls.path(
        "api/sourceitem/orders/", i_views.APISourceItemOrdersView.as_view(), name="api_sourceitem_orders"),
    urls.path(
        "api/sourceitem/quantity_adjustment/", i_views.APISourceItemQuantityAdjustmentView.as_view(),
        name="api_sourceitem_quantity_adjustment"),
    urls.path(
        "api/sourceitem/wide_filter/", i_views.APISourceItemWideFilterView.as_view(), name="api_sourceitem_widefilter"),

    urls.path("reports/common_name_prices/", i_views.ReportsCommonNamePricesView.as_view(), name="reports_common_name_prices"),
    urls.path("reports/created_today/", i_views.ReportsCreatedTodayView.as_view(), name="reports_created_today"),
    urls.path("reports/debug_sourceitem_list/", i_views.ReportsDebugSourceItemListView.as_view(), name="debug_sourceitem_list"),
    urls.path("reports/duplicate_items/", i_views.ReportsDuplicateItemsView.as_view(), name="reports_duplicate_items"),
    urls.path(
        "reports/orders_created_range/", i_views.ReportsOrdersCreatedRangeView.as_view(),
        name="reports_orders_created_range"),
    urls.path(
        "reports/orders_created_times_last_week/", i_views.ReportsCreatedTimesLastWeekView.as_view(),
        name="reports_orders_created_times_last_week"),
    urls.path("reports/packaging_costs/", i_views.ReportsPackagingCostsView.as_view(), name="reports_packaging_costs"),
    urls.path("reports/price_over_time/", i_views.ReportsPriceOverTimeView.as_view(), name="reports_price_over_time"),
    urls.path(
        "reports/source_categories/", i_views.ReportsSourceCategoriesView.as_view(), name="reports_source_categories"),
    urls.path("reports/source_totals/", i_views.ReportsSourceTotalsView.as_view(), name="reports_source_totals"),
    urls.path(
        "reports/source_totals_over_time/", i_views.ReportsSourceTotalsOverTimeView.as_view(), name="reports_source_totals_over_time"),

    urls.path(
        "saved_search/current_prices", i_views.SearchCriteriaCurrentPricesView.as_view(),
        name="saved_search_current_prices"),

    urls.path("sourceitem/mathcheck/", i_views.SourceItemMathCheckView.as_view(), name="sourceitem_mathcheck"),
    urls.path("sourceitem/orders/", i_views.SourceItemOrdersView.as_view(), name="sourceitem_orders"),
    urls.path(
        "sourceitem/order/<str:source>/<str:order_number>/<str:delivered_date>/",
        i_views.SourceItemOrderItemsView.as_view(), name="sourceitem_order_items_with_date"),
    urls.path(
        "sourceitem/order/<str:source>/<str:order_number>/", i_views.SourceItemOrderItemsView.as_view(),
        name="sourceitem_order_items"),
    urls.path("sourceitem/search/", i_views.SourceItemSearchView.as_view(), name="sourceitem_search"),
    urls.path("sourceitem/search/save", i_views.SourceItemSaveSearchView.as_view(), name="sourceitem_save_search"),
    urls.path("sourceitem/stats/", i_views.SourceItemStatsView.as_view(), name="sourceitem_stats"),
    urls.path("sourceitem/create/", i_views.SourceItemCreateView.as_view(), name="sourceitem_create"),
]
