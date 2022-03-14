from django import urls
from django.views import generic

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path("api_rawincomingorders/", i_views.APIRawIncomingOrderListView.as_view(), name="api_rawincomingorder_list"),
    urls.path("api_rawincomingitems/", i_views.APIRawIncomingItemListView.as_view(), name="api_rawincomingitem_list"),
    urls.path("api_rawincomingitem/<uuid:pk>/", i_views.APIRawIncomingItemDetailView.as_view(), name="api_rawincomingitem_detail"),

    urls.path("rawincomingitems/", i_views.RawIncomingItemListView.as_view(), name="rawincomingitem_list"),
    urls.path("rawincomingitem/new/", i_views.RawIncomingItemCreateView.as_view(), name="rawincomingitem_new"),
    urls.path("rawincomingitem/<uuid:pk>/update", i_views.RawIncomingItemUpdateView.as_view(), name="rawincomingitem_update"),
    urls.path("rawincomingitem/<uuid:pk>/delete", i_views.RawIncomingItemDeleteView.as_view(), name="rawincomingitem_delete"),
    urls.path("rawincomingitem/<uuid:pk>/", i_views.RawIncomingItemDetailView.as_view(), name="rawincomingitem_detail"),
    urls.path("", generic.RedirectView.as_view(pattern_name="inventory:rawincomingitem_list", permanent=False), name="home"),
]
