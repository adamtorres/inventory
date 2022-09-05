"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import urls
from django.contrib import admin
from django.urls import path
from django.views import generic

from . import views


urlpatterns = [
    path('messages/', urls.include('drf_messages.urls')),

    path('admin/', admin.site.urls),
    # urls.path('news/', urls.include('news.urls', namespace='news')),

    path('inventory/', urls.include('inventory.urls', namespace="inventory")),

    path('', generic.RedirectView.as_view(
        pattern_name="inventory:sourceitem_search", permanent=False), name="homepage"),
    # Redirect a path-less url to a specific page without it being permanent.
    # path('', generic.RedirectView.as_view(pattern_name="app:urlname", permanent=False), name="homepage"),
]
