from django import urls
from django.views import generic

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path("api_item_with_in_stock/", i_views.APIItemInStockView.as_view(), name="api_iteminstock_list"),
    urls.path("api_item_with_in_stock/<uuid:pk>/", i_views.APIItemInStockView.as_view(), name="api_iteminstock_detail"),
    urls.path("api_item_with_in_stock_quantities/", i_views.APIItemWithInStockQuantities.as_view(), name="api_itemwithinstockquantities_list"),
    urls.path("api_common_item_with_in_stock_quantities/<uuid:pk>/", i_views.APICommonItemWithInStockQuantities.as_view(), name="api_commonitemwithinstockquantities_detail"),
    urls.path("api_common_item_with_in_stock_quantities/", i_views.APICommonItemWithInStockQuantities.as_view(), name="api_commonitemwithinstockquantities_list"),

    urls.path("api_rawincomingorders/", i_views.APIRawIncomingOrderListView.as_view(), name="api_rawincomingorder_list"),
    urls.path("api_rawincomingorder/<uuid:pk>/", i_views.APIRawIncomingOrderDetailView.as_view(), name="api_rawincomingorder_detail"),

    urls.path("api_rawincomingitems/", i_views.APIRawIncomingItemListView.as_view(), name="api_rawincomingitem_list"),
    urls.path("api_rawincomingitem/<uuid:pk>/", i_views.APIRawIncomingItemDetailView.as_view(), name="api_rawincomingitem_detail"),

    urls.path("api_rawitem/wide_filter/", i_views.RawItemWideFilterView.as_view(), name="api_rawitem_widefilter"),
    urls.path("api_rawincomingitem/wide_filter/", i_views.RawIncomingItemWideFilterView.as_view(), name="api_rawincomingitem_widefilter"),

    urls.path("item_in_stock/", i_views.ItemInStockListView.as_view(), name="item_in_stock_list"),
    urls.path("item_in_stock/<uuid:pk>/", i_views.ItemInStockDetailView.as_view(), name="item_in_stock_detail"),

    urls.path("random_stats/", i_views.RandomStatsView.as_view(), name="random_stats"),

    urls.path("rawincomingorders/", i_views.RawIncomingOrderListView.as_view(), name="rawincomingorder_list"),
    urls.path("rawincomingorder/<uuid:pk>/", i_views.RawIncomingOrderDetailView.as_view(), name="rawincomingorder_detail"),

    urls.path("rawincomingitems/", i_views.RawIncomingItemListView.as_view(), name="rawincomingitem_list"),
    urls.path("rawincomingitems/lookup/", i_views.RawIncomingItemLookupView.as_view(), name="rawincomingitem_lookup"),
    urls.path("rawincomingitem/new/", i_views.RawIncomingItemCreateView.as_view(), name="rawincomingitem_new"),
    urls.path("rawincomingitem/<uuid:pk>/update", i_views.RawIncomingItemUpdateView.as_view(), name="rawincomingitem_update"),
    urls.path("rawincomingitem/<uuid:pk>/delete", i_views.RawIncomingItemDeleteView.as_view(), name="rawincomingitem_delete"),
    urls.path("rawincomingitem/<uuid:pk>/", i_views.RawIncomingItemDetailView.as_view(), name="rawincomingitem_detail"),
    urls.path("", generic.RedirectView.as_view(pattern_name="inventory:rawincomingitem_lookup", permanent=False), name="home"),
]
