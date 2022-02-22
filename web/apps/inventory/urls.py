from django.urls import path

from . import views


urlpatterns = [
    path('', views.InventoryView.as_view(), name="inventory_list"),
    path('usage/<int:year>/', views.ChangeView.as_view()),
    path('usage/<int:year>/<int:month>/', views.ChangeView.as_view()),
    path('usage/<int:year>/<int:month>/<slug:slug>/', views.ChangeView.as_view()),
    path('locations/', views.LocationView.as_view(), name="locations"),
    path('usagereport/add', views.UsageReportCreate.as_view(), name="usage_report_add"),
    path('usagereport/<uuid:pk>/', views.UsageReportDetail.as_view(), name="usage_report"),
    path('usagereports/', views.UsageReportList.as_view(), name="usage_reports"),
]
