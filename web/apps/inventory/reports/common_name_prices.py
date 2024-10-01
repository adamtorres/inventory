from django.db import connections


class CommonNamePrices(object):
    @staticmethod
    def run():
        sql = "SELECT * FROM common_name_prices('2023-01-01', '2025-01-01');"
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
