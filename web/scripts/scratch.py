from django.db import models

from inventory import models as inv_models


def validate_items():
    qs = inv_models.RawIncomingItem.objects.ready_to_create()
    # { 'source': <Source: gem>,
    #   'category': <Category: paper & disp>,
    #   'name': 'foam squat container 12oz (20 series lid) 20/25',
    #   'unit_size': '25ct',
    #   'pack_quantity': Decimal('20.0000'),
    #   'item_code': 'dar12sj20'}
    q = inv_models.RawIncomingItem.objects.get_raw_item_filter(qs=qs)
    for dupe_item in inv_models.RawItem.objects.filter(q):
        print("\t".join(
            [f"{field}={getattr(dupe_item, field)!r}" for field in ['source', 'name', 'unit_size', 'pack_quantity']]))


    new_item_list = inv_models.RawIncomingItem.objects.items(qs=qs, only_new=True)


# DETAIL:  Key (source_id, name, unit_size, pack_quantity)=(
#   2bcc9138-bfab-47ab-8c85-1650cbf088b4, bbrlcls ham pit bnls hckry smkd, 14-19#, 2.0000) already exists.


def run():
    validate_items()
