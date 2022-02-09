from django.urls import path

from . import views


urlpatterns = [
    path('', views.BasicDashboardView.as_view(), name="dashboard"),
]
