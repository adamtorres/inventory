import pathlib

from django.db import migrations

forward_sql = (pathlib.Path(__file__).parent.parent / 'sql/source_totals_over_time-0001.sql').read_text()

reverse_sql = """
DROP FUNCTION IF EXISTS source_totals_over_time(start_date DATE, end_date DATE);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_vw_order_created_times_last_week_0001'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql),
    ]
