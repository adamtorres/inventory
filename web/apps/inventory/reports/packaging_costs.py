from .. import models as inv_models


class PackagingCosts(object):
    @staticmethod
    def run():
        # Names of the SearchCriteria objects and an int to set the sort order on the report.
        saved_search_names = {
            "Saddle pack bag": 0,
            "Paper bag": 1,
            "Senior Tray": 2,
            "Foam 1 compartment": 3,
            "Foam 3 compartment": 4,
            "Foam 8oz squat container": 5,
            "Foam 12oz squat container": 6,
            "Vented lid for 8oz and 12oz foam": 7,
            "Plastic 8oz container with lid": 8,
        }
        report_data = []
        qs = inv_models.SearchCriteria.objects.filter(name__in=saved_search_names.keys())
        sorted_qs = sorted(qs, key=lambda x: saved_search_names[x.name])
        for ss in sorted_qs:
            item = ss.get_last_result()
            item_name = item.verbose_name or item.cryptic_name
            report_data.append({
                'name': item_name, 'description': ss.description, 'last_order_date': item.delivered_date,
                'quantity': (item.pack_quantity * item.unit_quantity), 'pack_cost': item.pack_cost,
                'per_use_cost': item.per_use_cost(),
                "item_code": item.item_code, "source_id": item.source_id, "delivered_date": item.delivered_date,
                "order_number": item.order_number,
            })
        return report_data
