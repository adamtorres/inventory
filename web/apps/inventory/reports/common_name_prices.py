from django.db import connections


class CommonNamePrices(object):
    @staticmethod
    def run():
        # Date range is set to include all data I have been able to track down.  Might make this a setting later.
        sql = """
        SELECT * FROM common_name_prices('2021-01-01'::DATE, (CURRENT_TIMESTAMP::DATE + '1 day'::INTERVAL)::DATE);
        """
        with connections['default'].cursor() as cur:
            cur.execute(sql)
            headers = [c.name for c in cur.description]
            table_data = []
            for rec in cur.fetchall():
                tmp = {h: c for h, c in zip(headers, rec)}
                table_data.append(tmp)
            return table_data
