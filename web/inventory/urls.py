from django import urls
from django.views import generic

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path("rawincomingitems/", i_views.RawIncomingItemView.as_view(), name="rawincomingitem_list"),
    # urls.path("article/new/", n_views.ArticleCreateView.as_view(), name="article_new"),
    # urls.path("article/<uuid:pk>/", n_views.ArticleDetailView.as_view(), name="article_detail"),
    # urls.path("article/<uuid:pk>/delete", n_views.ArticleDeleteView.as_view(), name="article_delete"),
    # urls.path("article/<uuid:pk>/update", n_views.ArticleUpdateView.as_view(), name="article_update"),
    urls.path("", generic.RedirectView.as_view(pattern_name="inventory:rawincomingitem_list", permanent=False), name="home"),
]
