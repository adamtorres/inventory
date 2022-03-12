from django import urls

from . import views as n_views


app_name = "news"

urlpatterns = [
    urls.path("", n_views.HomeView.as_view(), name="home"),
    urls.path("articles/", n_views.ArticleListView.as_view(), name="article_list"),
    urls.path("article/new/", n_views.ArticleCreateView.as_view(), name="article_new"),
    urls.path("article/<uuid:pk>/", n_views.ArticleDetailView.as_view(), name="article_detail"),
    urls.path("article/<uuid:pk>/delete", n_views.ArticleDeleteView.as_view(), name="article_delete"),
    urls.path("article/<uuid:pk>/update", n_views.ArticleUpdateView.as_view(), name="article_update"),

    urls.path("authors/", n_views.AuthorListView.as_view(), name="author_list"),
    urls.path("author/new/", n_views.AuthorCreateView.as_view(), name="author_new"),
    urls.path("author/<uuid:pk>/", n_views.AuthorDetailView.as_view(), name="author_detail"),
    urls.path("author/<uuid:pk>/delete", n_views.AuthorDeleteView.as_view(), name="author_delete"),
    urls.path("author/<uuid:pk>/update", n_views.AuthorUpdateView.as_view(), name="author_update"),
]
