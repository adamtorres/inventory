from django.db import models
from .. import models as inv_models


class DebugSourceItemList(object):
    @staticmethod
    def run():
        """
        Selects very specific items.  Useful when making migration changes so I can see how different sample items are
        affected.
        """
        criteria = [
            {
                # FireCLS beef grnd bulk 81/19 chub F
                "delivered_date": "2021-01-07", "order_number": "385339824", "item_code": "0566838"},
            {
                # tomato large
                "delivered_date": "2022-07-20", "order_number": "02-2031852", "item_code": "3151"},
            {
                # BBRLCLS beef roast top rnd c/o sp
                "delivered_date": "2021-03-04", "order_number": "385429425", "item_code": "0042705"},
            {
                # BBRLCLS beef corned brskt raw 30%
                "delivered_date": "2021-03-04", "order_number": "385429425", "item_code": "5950076"},
            {
                # Packer apple red del wa xfcy frsh
                "delivered_date": "2021-01-07", "order_number": "385339824", "item_code": "3284615"},
            {
                # Daristr milk low fat 1%
                "delivered_date": "2021-01-07", "order_number": "385339824", "item_code": "3441803"},
            {
                # SYS CLS chicken brst IFZ marn ziploc
                "delivered_date": "2021-01-14", "order_number": "385349943", "item_code": "9562877"},
            {
                # BBRLCLS chip potato reg
                "delivered_date": "2021-01-21", "order_number": "385359942", "item_code": "7073973"},
            {
                # AREZIMP cheese mozz string
                "delivered_date": "2021-01-21", "order_number": "385359942", "item_code": "4384214"},
            {
                # firerel beef patty 80/20 rnd frz
                "delivered_date": "2022-07-14", "order_number": "485350026", "item_code": "1114016"},
            {
                # SYS CLS Flour All Purp H&R BL E
                "delivered_date": "2021-01-14", "order_number": "385349943", "item_code": "8378111"},
            {
                # Nabisco cookie crumb oreo med
                "delivered_date": "2021-01-14", "order_number": "385349944", "item_code": "5524137"},
            {
                # BKRSCLS sugar confectioner 10x cane
                "delivered_date": "2021-03-04", "order_number": "385429424", "item_code": "5825672"},
            {
                # dailys bacon layflat 14/16ct
                "delivered_date": "2021-04-15", "order_number": "385497159", "item_code": "2133940"},
            {
                # BBRLCLS cheese american 96 SLI YEL
                "delivered_date": "2021-01-14", "order_number": "385349943", "item_code": "5132273"},
            {
                # SYS REL broccoli spear poly
                "delivered_date": "2021-01-07", "order_number": "385339824", "item_code": "6743058"},
            {
                # SYS CLS bean green cut 4sv bl fcy
                "delivered_date": "2021-01-07", "order_number": "385339824", "item_code": "4062394"},
            {
                # swtbaby sauce bbq original
                "delivered_date": "2021-01-14", "order_number": "385349943", "item_code": "3369388"},
            {
                # whlfimp butter solid sltd usda aa
                "delivered_date": "2021-01-21", "order_number": "385359943", "item_code": "3030816"},
            {
                # SYS IMP pan coating arsl conc
                "delivered_date": "2021-02-25", "order_number": "385416253", "item_code": "4290049"},
            {
                # SYS REL mix cake white complt
                "delivered_date": "2021-01-14", "order_number": "385349944", "item_code": "5301601"},
            {
                # WHLFCLS cream sour cultrd grade a
                "delivered_date": "2021-01-07", "order_number": "385339824", "item_code": "5020193"},
            {
                # whlfimp cheese cream loaf
                "delivered_date": "2021-01-21", "order_number": "385359943", "item_code": "1012566"},
            {
                # SOLO cup plas prtn clr 2oz
                "delivered_date": "2021-05-06", "order_number": "385531435", "item_code": "1213859"},
            {
                # PACTIV lid plas clr prtn f/ 2Z
                "delivered_date": "2021-05-06", "order_number": "385531435", "item_code": "7819764"},
        ]
        selected_item_filter = models.Q()
        for crit in criteria:
            selected_item_filter |= models.Q(**crit)
        return inv_models.SourceItem.objects.filter(selected_item_filter).order_by("total_weight", "unit_quantity")
