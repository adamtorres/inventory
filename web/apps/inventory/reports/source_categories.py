from django.db import connections


class SourceCategories(object):
    @staticmethod
    def run():
        sql = """
        SELECT source_category,
            COUNT(1) AS items, COUNT(DISTINCT FORMAT('%s|%s|%s', source_id, order_number, delivered_date)) AS orders,
            MIN(delivered_date) AS first_delivered, MAX(delivered_date) AS last_delivered,
            SUM(extended_cost) AS extended_cost
        FROM inventory_sourceitem
        GROUP BY source_category
        ORDER BY source_category;"""
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
