from django.conf import urls
from django.contrib import admin
from django.urls import path
from django.views import generic


urlpatterns = [
    path('grappelli/', urls.include('grappelli.urls')),
    path('grappelli-docs/', urls.include('grappelli.urls_docs')), # grappelli docs URLS
    path('admin/', admin.site.urls),
    path('inventory/', urls.include('inventory.urls', namespace="inventory")),
    path('', generic.RedirectView.as_view(pattern_name="inventory:home", permanent=False), name="homepage"),
]
