from django.urls import path

from . import views


urlpatterns = [
    path('groups/', views.IncomingGroupView.as_view(), name='incoming_groups'),
    # path('groups/', views.IncomingGroupListView.as_view(), name="incoming_groups"),
    path('group/<uuid:pk>/edit', views.IncomingGroupUpdateView.as_view(), name='incoming_group_edit'),
    path('group/<uuid:pk>/', views.IncomingGroupDetailView.as_view(), name='incoming_group'),
    path('group/', views.IncomingGroupCreateView.as_view(), name='incoming_group_create'),
    path('group/ex_create/', views.ExampleIncomingItemGroupCreateView.as_view(), name='ex_create'),
    path('group/<uuid:pk>/ex_edit', views.ExampleIncomingItemGroupEditView.as_view(), name='ex_edit'),
    path('items/autocomplete', views.AutocompleteItemView.as_view(), name='inc_autocomplete_items'),
    path('incomingitems/autocomplete', views.AutocompleteIncomingItemsView.as_view(), name='inc_autocomplete_incomingitems'),
    path('items/live_filter', views.FilterItemView.as_view(), name='inc_live_filter_items'),
    path('incomingitems/live_filter', views.FilterIncomingItemsView.as_view(), name='inc_live_filter_incomingitems'),
    path('incomingitems/lookup/', views.IncomingGroupItemLookupView.as_view(), name='incoming_group_item_lookup'),
]
