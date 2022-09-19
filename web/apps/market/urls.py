from django import urls

from . import views as m_views


app_name = "market"

urlpatterns = [
    urls.path("items/", m_views.ItemListView.as_view(), name="item_list"),
    urls.path("item/<uuid:pk>", m_views.ItemDetailView.as_view(), name="item_detail"),
    urls.path("item/new", m_views.ItemCreateView.as_view(), name="item_create"),
    urls.path("item_packs/", m_views.ItemPackListView.as_view(), name="item_pack_list"),
    urls.path("item_pack/<uuid:pk>", m_views.ItemPackDetailView.as_view(), name="item_pack_detail"),
    urls.path("item_pack/new", m_views.ItemPackCreateView.as_view(), name="item_pack_create"),
    urls.path("orders/", m_views.OrderListView.as_view(), name="order_list"),
    urls.path("order/<uuid:pk>", m_views.OrderDetailView.as_view(), name="order_detail"),
    urls.path("order/<uuid:pk>/modify", m_views.OrderModifyByActionView.as_view(), name="order_modify"),
    urls.path("order/new", m_views.OrderCreateView.as_view(), name="order_create"),
    urls.path("order/<uuid:pk>/line_items", m_views.OrderLineItemCreateView.as_view(), name="order_line_item_edit"),
]