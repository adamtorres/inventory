from django import urls
from django.views import generic

from incoming import models as inc_models


class IncomingGroupItemLookupView(generic.TemplateView):
    template_name = "incoming/incoming_group_item_lookup.html"
