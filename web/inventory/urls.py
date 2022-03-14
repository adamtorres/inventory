from django import urls
from django.views import generic

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path("api_rawincomingitems/", i_views.APIRawIncomingItemListView.as_view(), name="api_rawincomingitem_list"),
    urls.path("api_rawincomingitem/<uuid:pk>/", i_views.APIRawIncomingItemDetailView.as_view(), name="api_rawincomingitem_detail"),

    urls.path("rawincomingitems/", i_views.RawIncomingItemListViewAlt.as_view(), name="rawincomingitem_list"),
    urls.path("rawincomingitem/<uuid:pk>/", i_views.RawIncomingItemDetailView.as_view(), name="rawincomingitem_detail"),
    # urls.path("article/new/", n_views.ArticleCreateView.as_view(), name="article_new"),
    # urls.path("article/<uuid:pk>/delete", n_views.ArticleDeleteView.as_view(), name="article_delete"),
    # urls.path("article/<uuid:pk>/update", n_views.ArticleUpdateView.as_view(), name="article_update"),
    urls.path(
        "", generic.RedirectView.as_view(pattern_name="inventory:api_rawincomingitem_list", permanent=False),
        name="home"),
]
