from django.db import connections


def run_line_report_sql(sql, start_date, end_date, label_field, **kwargs):
    sql_kwargs = {'start_date': start_date, 'end_date': end_date}
    # TODO: check for copied lists and such.  We aren't modifying them so not expecting issues.
    sql_kwargs.update(kwargs)
    with connections['default'].cursor() as cur:
        cur.execute(sql, sql_kwargs)
        headers = [c.name for c in cur.description]
        table_data = []
        line_data = []
        for rec in cur.fetchall():
            tmp = {h: c for h, c in zip(headers, rec)}
            table_data.append(tmp)
            # Assume any list field is a data list and give it the column's name.
            data_tmp = {
                "label": "",
            }
            for f, v in tmp.items():
                # orders, total_count_quantity, total_unit_quantity, total_extended_price
                if f == label_field:
                    data_tmp['label'] = v
                if isinstance(v, list) or f == 'id':
                    data_tmp[f] = v
            line_data.append(data_tmp)
        return {
            "table": table_data,
            "data": line_data,
        }


def run_pie_report_sql(sql, start_date, end_date, pie_label_field, pie_data_field):
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
