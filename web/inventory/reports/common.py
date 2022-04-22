from django.db import connections


def run_report_sql(sql, start_date, end_date, pie_label_field, pie_data_field):
    with connections['default'].cursor() as cur:
        cur.execute(sql, {'start_date': start_date, 'end_date': end_date})
        headers = [c.name for c in cur.description]
        table_data = []
        pie_labels = []
        pie_label_idx = headers.index(pie_label_field)
        pie_data = []
        pie_data_idx = headers.index(pie_data_field)
        for rec in cur.fetchall():
            table_data.append({h: c for h, c in zip(headers, rec)})
            pie_labels.append(rec[pie_label_idx])
            pie_data.append(round(float(rec[pie_data_idx]), 2))
        return {
            "table": table_data,
            "labels": pie_labels,
            "data": pie_data,
        }
