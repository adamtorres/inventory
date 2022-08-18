from django import urls

from . import views as i_views


app_name = "inventory"

urlpatterns = [
    urls.path("sourceitem/search/", i_views.SourceItemSearchView.as_view(), name="sourceitem_search"),
]
