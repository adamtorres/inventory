from django import urls
from rest_framework import urlpatterns as rf_urls

from . import views as i_views


app_name = "inventory"

# api_chart_urls = [
#     urls.path("api/sourceitem/chartdata/", i_views.APIChartDataView.as_view(), name="api_sourceitem_chartdata"),
# ]
# api_chart_urls = rf_urls.format_suffix_patterns(api_chart_urls, allowed=['api', 'chartjs'])

urlpatterns = [
    urls.path(
        "api/sourceitem/autocomplete/", i_views.APISourceItemAutocompleteSearchView.as_view(),
        name="api_sourceitem_autocomplete"),

    urls.path("api/sourceitem/chartdata/", i_views.APIChartDataView.as_view(), name="api_sourceitem_chartdata"),

    urls.path(
        "api/sourceitem/orders/", i_views.APISourceItemOrdersView.as_view(), name="api_sourceitem_orders"),
    urls.path(
        "api/sourceitem/quantity_adjustment/", i_views.APISourceItemQuantityAdjustmentView.as_view(),
        name="api_sourceitem_quantity_adjustment"),
    urls.path(
        "api/sourceitem/wide_filter/", i_views.APISourceItemWideFilterView.as_view(), name="api_sourceitem_widefilter"),

    urls.path("reports/created_today/", i_views.ReportsCreatedTodayView.as_view(), name="reports_created_today"),
    urls.path("reports/price_over_time/", i_views.ReportsPriceOverTimeView.as_view(), name="reports_price_over_time"),

    urls.path("sourceitem/orders/", i_views.SourceItemOrdersView.as_view(), name="sourceitem_orders"),
    urls.path("sourceitem/order/<str:source>/<str:order_number>/<str:delivered_date>/", i_views.SourceItemOrderItemsView.as_view(), name="sourceitem_order_items_with_date"),
    urls.path("sourceitem/order/<str:source>/<str:order_number>/", i_views.SourceItemOrderItemsView.as_view(), name="sourceitem_order_items"),
    urls.path("sourceitem/search/", i_views.SourceItemSearchView.as_view(), name="sourceitem_search"),
    urls.path("sourceitem/stats/", i_views.SourceItemStatsView.as_view(), name="sourceitem_stats"),
    urls.path("sourceitem/create/", i_views.SourceItemCreateView.as_view(), name="sourceitem_create"),
]
