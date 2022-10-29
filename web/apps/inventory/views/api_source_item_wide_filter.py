
from scrap import views as sc_views

from inventory import models as inv_models, serializers as inv_serializers


class APISourceItemWideFilterView(sc_views.WideFilterView):
    model = inv_models.SourceItem
    serializer = inv_serializers.SourceItemWideFilterSerializer
    order_fields = ['-delivered_date', 'source', 'order_number', 'line_item_number']
    prefetch_fields = ['source']
