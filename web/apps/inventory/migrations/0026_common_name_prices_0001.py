import pathlib

from django.db import migrations

forward_sql = (pathlib.Path(__file__).parent.parent / 'sql/common_name_prices-0001.sql').read_text()

reverse_sql = """
DROP FUNCTION IF EXISTS common_name_prices(start_date DATE, end_date DATE);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_source_orders_0001'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql),
    ]
