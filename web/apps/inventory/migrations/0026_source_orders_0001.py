import pathlib

from django.db import migrations

forward_sql = (pathlib.Path(__file__).parent.parent / 'sql/source_orders-0001.sql').read_text()

reverse_sql = """
DROP FUNCTION IF EXISTS source_orders(start_date DATE, end_date DATE);
"""


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_common_name_prices_0001'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql),
    ]
