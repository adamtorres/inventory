from .common import run_table_report_sql


def get_item_price_change_report(start_date, end_date, items: list):
    sql = """
    SELECT *
    FROM f_item_price_change_report(%(start_date)s, %(end_date)s, %(selected_items)s);
    """
    data = run_table_report_sql(sql, start_date, end_date, selected_items=items)
    min_date = None
    max_date = None
    for row in data['table']:
        if min_date is None or min_date > row['first_order']:
            min_date = row['first_order']
        if max_date is None or max_date < row['last_order']:
            max_date = row['last_order']
    data['settings'] = {
        'start_date': start_date,
        'end_date': end_date,
        'items': items,
    }
    data['stats'] = {
        'min_date': min_date,
        'max_date': max_date,
    }
    return data

# from inventory import reports as inv_reports
# from scrap import utils as sc_utils
# items = ["butter", "ground beef", "cut green beans", "hamburger sesame buns", "semi sweet chocolate chips", "flour"]
# inv_reports.get_item_price_change_report(*sc_utils.get_monthly_date_range(6), items)
# id, source_name, category_name, commonitem_name, ticked_item_code, name, pack_quantity, unit_size, unit_quantity,
# first_order, first_pack_price, first_price_per_count, last_order, last_pack_price, last_price_per_count,
# pack_price_change, orders, total_spent
