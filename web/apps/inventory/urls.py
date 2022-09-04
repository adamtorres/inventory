from django import urls

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path(
        "api/sourceitem/wide_filter/", i_views.SourceItemWideFilterView.as_view(), name="api_sourceitem_widefilter"),
    urls.path(
        "api/sourceitem/quantity_adjustment/", i_views.SourceItemQuantityAdjustmentView.as_view(),
        name="api_sourceitem_quantity_adjustment"),

    urls.path("sourceitem/search/", i_views.SourceItemSearchView.as_view(), name="sourceitem_search"),
    urls.path("sourceitem/stats/", i_views.SourceItemStatsView.as_view(), name="sourceitem_stats"),
]
