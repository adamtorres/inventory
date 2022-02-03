from django.views import generic

from inventory import models as inv_models


class InventoryView(generic.TemplateView):
    template_name = "inventory/list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs.update({
            'hello': "some data",
        })
        qs = inv_models.Item.objects.get_consolidated_inventory()
        # QuerySet of:
        # {
        #   'common_item': UUID('4c6a3ce1-8a24-48c7-9d1c-249394a3a381'),
        #   'common_item_name': 'ground beef',
        #   'other_names': 'hamburger, hamburger meat, ground meat',
        #   'quantity': Decimal('3.0000')
        # }
        kwargs['inventory'] = {i['common_item_name']: i for i in qs}
        return kwargs
