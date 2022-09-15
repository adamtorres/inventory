from django import urls

from . import views as m_views


app_name = "market"

urlpatterns = [
    urls.path("items/", m_views.ItemListView.as_view(), name="item_list"),
    urls.path("item/<uuid:pk>", m_views.ItemDetailView.as_view(), name="item_detail"),
    urls.path("item/new", m_views.ItemCreateView.as_view(), name="item_create"),
]