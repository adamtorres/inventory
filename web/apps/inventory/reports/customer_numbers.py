from django.db import connections


class CustomerNumbers(object):
    @staticmethod
    def run():
        sql = """
select inv_s.name, inv_si.customer_number,
       count(1) as items,
       count(distinct format('%s|%s|%s', source_id, order_number, delivered_date)) as orders
from inventory_sourceitem inv_si
join inventory_source as inv_s
on inv_si.source_id = inv_s.id
group by inv_s.name, inv_si.customer_number
order by inv_s.name, inv_si.customer_number;
"""
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
