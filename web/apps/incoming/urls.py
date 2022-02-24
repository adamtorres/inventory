from django.urls import path

from . import views


urlpatterns = [
    path('incominggroups/', views.IncomingGroupView.as_view(), name='incoming_groups'),
    # path('incominggroups/', views.IncomingGroupListView.as_view(), name="incoming_groups"),
    path('incominggroup/<uuid:pk>/edit', views.IncomingGroupUpdateView.as_view(), name='incoming_group_edit'),
    path('incominggroup/<uuid:pk>/', views.IncomingGroupDetailView.as_view(), name='incoming_group'),
    path('incominggroup/', views.IncomingGroupCreateView.as_view(), name='incoming_group_create'),
    path('incominggroup/ex_create/', views.ExampleIncomingItemGroupCreateView.as_view(), name='ex_create'),
    path('incominggroup/<uuid:pk>/ex_edit', views.ExampleIncomingItemGroupEditView.as_view(), name='ex_edit'),
    path('incoming/autocomplete', views.AutocompleteView.as_view(), name='autocomplete'),
    path('incominggroupitem/lookup/', views.IncomingGroupItemLookupView.as_view(), name='incoming_group_item_lookup'),
]
