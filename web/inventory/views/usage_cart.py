import requests

from django import urls, shortcuts
from django.views import generic

from inventory import models as inv_models, serializers as inv_serializers
from inventory.views import mixins as inv_mixins
from scrap import views as sc_views


class UsageCartView(inv_mixins.UsageCartData, sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/usage_cart.html"
    on_page_title = "Usage Cart"

    def post(self, request, *args, **kwargs):
        if not request.session.get('used_items'):
            # No items.  Just redirect.
            return shortcuts.redirect(urls.reverse("inventory:usage_cart"))
        ug_data = {k: v for k, v in request.POST.items() if k in ['description', 'when', 'comment']}
        ui_data = {k[-36:]: v for k, v in request.POST.items() if k.startswith('item-comment-')}
        ug_s = inv_serializers.UsageGroupSerializer(data=ug_data)
        if ug_s.is_valid():
            usage_group_obj = ug_s.save()
            used_items = []
            for item_id, use_count in request.session['used_items'].items():
                used_items.append({
                    'item_in_stock': item_id, 'used_quantity': use_count, 'usage_group': usage_group_obj.id,
                    'comment': ui_data.get(item_id) or ''
                })
            # TODO: make this create via api?  If not, why have I been making API calls all this time?
            ui_s = inv_serializers.CreateUsageSerializer(data=used_items, many=True)
            if ui_s.is_valid():
                used_item_objs = ui_s.save()
                item_in_stock_to_update = []
                for item in used_item_objs:
                    # TODO: If this were a multi-user application, we'd want to verify the needed quantity was still
                    #  available.
                    item.item_in_stock.remaining_unit_quantity -= item.used_quantity
                    item_in_stock_to_update.append(item.item_in_stock)
                inv_models.ItemInStock.objects.bulk_update(
                    item_in_stock_to_update, fields=('remaining_unit_quantity', ))
                request.session['used_items'] = {}
                request.session.modified = True

            else:
                print(f"serializer errors: {ui_s.errors}")
        return shortcuts.redirect(urls.reverse("inventory:usage_cart"))
