from django.urls import path

from . import views


urlpatterns = [
    path('incominggroups/', views.IncomingGroupListView.as_view(), name="incoming_groups"),
]
