from django.urls import path

from . import views


urlpatterns = [
    path('', views.InventoryView.as_view(), name="inventory_list"),
    path('usage/<int:year>/', views.ChangeView.as_view()),
    path('usage/<int:year>/<int:month>/', views.ChangeView.as_view()),
    path('usage/<int:year>/<int:month>/<slug:slug>/', views.ChangeView.as_view()),
    path('locations/', views.LocationView.as_view()),
]
