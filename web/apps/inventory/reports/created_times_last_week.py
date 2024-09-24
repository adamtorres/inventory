from django.db import connections


class CreatedTimesLastWeek(object):
    @staticmethod
    def run():
        sql = "SELECT * FROM vw_order_created_times_last_week;"
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
