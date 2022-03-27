import requests

from django import urls
from django.views import generic

from inventory import models as inv_models
from inventory.views import mixins as inv_mixins
from scrap import views as sc_views


class UsageCartView(inv_mixins.UsageCartData, sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/usage_cart.html"
    on_page_title = "Usage Cart"
