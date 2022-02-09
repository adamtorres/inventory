from django.db import models
from django.views import generic

from inventory import models as inv_models


class LocationView(generic.TemplateView):
    template_name = "locations/summary.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['locations'] = []
        for l in inv_models.Location.objects.all():
            location_data = {
                'name': l.name,
                'cost': 0,
                'top_items': [],
            }
            # Calculate extended cost for each item in the location.
            qs = l.items.annotate(cost=models.F('unit_cost')*models.F('current_quantity'))
            # Sum up the extended cost for all items in this location.
            location_data['cost'] = qs.aggregate(location_cost=models.Sum('cost'))['location_cost']
            # get top items
            qs = qs.annotate(item_name=models.F('common_item__name'))
            qs = qs.values('item_name', 'unit_size')
            qs = qs.annotate(xcost=models.Sum('cost'), xquantity=models.Sum('current_quantity'))
            # TODO: validate these numbers
            for item in qs.order_by('-xcost')[:10]:
                location_data['top_items'].append({
                    'name': item['item_name'],
                    'quantity': item['xquantity'],
                    'cost': item['xcost'],
                })
            kwargs['locations'].append(location_data)
        return kwargs
