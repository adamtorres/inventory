from .common import run_table_report_sql


def get_item_price_change_report(start_date, end_date, items: list):
    sql = """
    SELECT *
    FROM f_item_price_change_report(%(start_date)s, %(end_date)s, %(selected_items)s);
    """
    return run_table_report_sql(sql, start_date, end_date, selected_items=items)

# from inventory import reports as inv_reports
# from scrap import utils as sc_utils
# items = ["butter", "ground beef", "cut green beans", "hamburger sesame buns", "semi sweet chocolate chips", "flour"]
# inv_reports.get_item_price_change_report(*sc_utils.get_monthly_date_range(6), items)
# id, source_name, category_name, commonitem_name, ticked_item_code, name, pack_quantity, unit_size, unit_quantity,
# first_order, first_pack_price, first_price_per_count, last_order, last_pack_price, last_price_per_count,
# pack_price_change, orders, total_spent
