from django.db import connections


class SourceCategories(object):
    @staticmethod
    def run():
        sql = """
        select source_category,
            count(1) as items, count(distinct format('%s|%s|%s', source_id, order_number, delivered_date)) as orders,
            min(delivered_date) as first_delivered, max(delivered_date) as last_delivered
        from inventory_sourceitem
        group by source_category
        order by source_category;"""
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
