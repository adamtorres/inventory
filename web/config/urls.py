"""inventory URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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

urlpatterns = [
    path('grappelli/', urls.include('grappelli.urls')),
    path('grappelli-docs/', urls.include('grappelli.urls_docs')), # grappelli docs URLS
    path('admin/', admin.site.urls),
    path('dashboard/', urls.include('dashboard.urls')),
    path('', urls.include('inventory.urls')),
    path('', urls.include('incoming.urls')),
]
