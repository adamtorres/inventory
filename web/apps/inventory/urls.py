from django.urls import path

from . import views


urlpatterns = [
    path('', views.InventoryView.as_view(), name="inventory_list"),
    path('usage/<int:year>/', views.ChangeView.as_view()),
    path('usage/<int:year>/<int:month>/', views.ChangeView.as_view()),
    path('usage/<int:year>/<int:month>/<slug:slug>/', views.ChangeView.as_view()),
    path('locations/', views.LocationView.as_view(), name="locations"),
    path('usagereport/add', views.UsageReportCreateView.as_view(), name="usage_report_add"),
    path('usagereport/<uuid:pk>/', views.UsageReportDetailView.as_view(), name="usage_report"),
    path('usagereport/<uuid:pk>/edit', views.UsageReportEditView.as_view(), name="usage_report_edit"),
    path('usagereports/', views.UsageReportListView.as_view(), name="usage_reports"),
    path('items/autocomplete', views.AutocompleteView.as_view(), name="inv_autocomplete"),
    path('commonitems/autocomplete', views.AutocompleteCommonItemView.as_view(), name="inv_autocomplete_commonitem"),
]
