from django.urls import path

from . import views


urlpatterns = [
    path('incominggroups/', views.IncomingGroupView.as_view(), name='incoming_groups'),
    # path('incominggroups/', views.IncomingGroupListView.as_view(), name="incoming_groups"),
    path('incominggroup/<uuid:pk>/edit', views.IncomingGroupUpdateView.as_view(), name='incoming_group_edit'),
    path('incominggroup/<uuid:pk>/', views.IncomingGroupDetailView.as_view(), name='incoming_group'),
    path('incominggroup/', views.IncomingGroupCreateView.as_view(), name='incoming_group_create'),
]
