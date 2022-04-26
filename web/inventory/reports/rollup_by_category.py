from .common import run_pie_report_sql


def get_rollup_by_category_data(start_date, end_date):
    sql = """
    SELECT *
    FROM f_rollup_by_category(%(start_date)s, %(end_date)s)
    ORDER BY "category";
    """
    pie_label_field = 'category'
    pie_data_field = 'extended_price'
    return run_pie_report_sql(sql, start_date, end_date, pie_label_field, pie_data_field)
