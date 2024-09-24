import pathlib

from django.db import migrations

forward_sql = (pathlib.Path(__file__).parent.parent / 'sql/vw_order_created_times_last_week-0001.sql').read_text()

reverse_sql = """
DROP VIEW IF EXISTS vw_order_created_times_last_week;
"""


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_searchcriteria_url_slug'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql),
    ]
