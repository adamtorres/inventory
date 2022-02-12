from django.urls import path

from . import views


urlpatterns = [
    path('incominggroups/', views.IncomingGroupListView.as_view(), name="incoming_groups"),
    path('incominggroup/<uuid:pk>/', views.IncomingGroupDetailView.as_view(), name='incoming_group'),
]
