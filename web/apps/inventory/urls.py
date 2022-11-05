from django import urls

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path(
        "api/sourceitem/autocomplete/", i_views.APISourceItemAutocompleteSearchView.as_view(),
        name="api_sourceitem_autocomplete"),
    urls.path(
        "api/sourceitem/orders/", i_views.APISourceItemOrdersView.as_view(), name="api_sourceitem_orders"),
    urls.path(
        "api/sourceitem/quantity_adjustment/", i_views.APISourceItemQuantityAdjustmentView.as_view(),
        name="api_sourceitem_quantity_adjustment"),
    urls.path(
        "api/sourceitem/wide_filter/", i_views.APISourceItemWideFilterView.as_view(), name="api_sourceitem_widefilter"),

    urls.path("sourceitem/orders/", i_views.SourceItemOrdersView.as_view(), name="sourceitem_orders"),
    urls.path("sourceitem/order/<str:source>/<str:order_number>/<str:delivered_date>/", i_views.SourceItemOrderItemsView.as_view(), name="sourceitem_order_items_with_date"),
    urls.path("sourceitem/order/<str:source>/<str:order_number>/", i_views.SourceItemOrderItemsView.as_view(), name="sourceitem_order_items"),
    urls.path("sourceitem/search/", i_views.SourceItemSearchView.as_view(), name="sourceitem_search"),
    urls.path("sourceitem/stats/", i_views.SourceItemStatsView.as_view(), name="sourceitem_stats"),
    urls.path("sourceitem/create/", i_views.SourceItemCreateView.as_view(), name="sourceitem_create"),
]
