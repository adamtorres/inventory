from django.views import generic

from inventory import models as inv_models


class InventoryView(generic.TemplateView):
    template_name = "inventory/list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        qs = inv_models.Item.objects.get_consolidated_inventory().order_by('category', 'locations', 'common_item_name')
        # QuerySet of:
        # {
        #     'common_item': UUID('4c6a3ce1-8a24-48c7-9d1c-249394a3a381'),
        #     'common_item_name': 'ground beef',
        #     'category': 'meats',
        #     'total_quantity': Decimal('3.0000'),
        #     'total_cost': Decimal('90.06000000'),
        #     'locations': 'Freezer, Refrigerator'}
        kwargs['inventory'] = {i['common_item_name']: i for i in qs}
        return kwargs
