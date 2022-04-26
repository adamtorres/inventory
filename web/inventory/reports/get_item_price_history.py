from .common import run_line_report_sql


def get_item_price_history(start_date, end_date, items: list):
    sql = """
    SELECT *
    FROM f_item_price_history(%(start_date)s, %(end_date)s, %(selected_items)s)
    ORDER BY category, name_and_unit_size;
    """
    return run_line_report_sql(sql, start_date, end_date, "name_and_unit_size", selected_items=items)

# from inventory import reports as inv_reports
# from scrap import utils as sc_utils
# items = ["butter", "ground beef", "cut green beans", "hamburger sesame buns", "semi sweet chocolate chips", "flour"]
# inv_reports.get_item_price_history(*sc_utils.get_monthly_date_range(6), items)
# id, category, name_and_unit_size, orders, total_count_quantity, total_unit_quantity, total_extended_price,
# first_count_price, first_unit_price
