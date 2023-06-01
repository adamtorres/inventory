from .. import models as inv_models


class PackagingCosts(object):
    @staticmethod
    def run():
        criteria = [
            {'item_code': 'elkdp657', 'name': ('saddle', ), 'description': 'roll bag, saddle bag, bag with flap'},
            {'item_code': 'baggk8500', 'name': ('paper', 'bag'), 'description': 'home delivery paper bag'},
            {'item_code': 'hfa204535250w', 'name': ('senior', 'tray'), 'description': 'senior tray, foil tray'},
            {'item_code': 'pctytd19901econ', 'name': ('foam', 'hinged'), 'description': 'large 1 comp foam'},
            {'item_code': 'pctytd19903econ', 'name': ('foam', 'hinged'), 'description': 'large 3 comp foam'},
            {'item_code': 'dar8sj20', 'name': ('foam', '8oz'), 'description': 'small foam cup'},
            {'item_code': 'dar12sj20', 'name': ('foam', '12oz'), 'description': 'large foam cup'},
            {'item_code': 'dar20jl', 'name': ('vented', 'lid'), 'description': 'lid for 8oz and 12oz foam'},
            {'item_code': 'lcpfpimdc8pp', 'name': ('deli', 'container'), 'description': 'small plastic cup'},
        ]
        report_data = []
        for crit in criteria:
            wide_filter_criteria = [('item_code', (crit['item_code'],)), ('name', crit['name'])]
            qs = inv_models.SourceItem.objects.wide_filter(wide_filter_criteria)
            qs = qs.exclude(delivered_quantity__lte=0)
            item = qs.first()
            item_name = item.verbose_name or item.cryptic_name
            report_data.append({
                'name': item_name, 'description': crit['description'], 'last_order_date': item.delivered_date,
                'quantity': (item.pack_quantity * item.unit_quantity), 'pack_cost': item.pack_cost,
                'per_use_cost': item.per_use_cost(),
            })
        return report_data
