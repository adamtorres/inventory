from django.db import connections


class CreatedToday(object):
    @staticmethod
    def run():
        sql = "SELECT * FROM vw_orders_entered_today;"
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
