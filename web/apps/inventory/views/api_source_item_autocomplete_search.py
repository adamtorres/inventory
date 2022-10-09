
from scrap import views as sc_views

from inventory import models as inv_models, serializers as inv_serializers


class SourceItemAutocompleteSearchView(sc_views.AutocompleteFilterView):
    # TODO: Should this include most recent order date?  Or is that too much?
    model = inv_models.SourceItem
    serializer = inv_serializers.SourceItemAutocompleteSerializer
    prefetch_fields = ['source']
