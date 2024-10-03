import pathlib

from django.db import migrations

forward_sql = (pathlib.Path(__file__).parent.parent / 'sql/common_name_prices-0002.sql').read_text()

reverse_sql = (pathlib.Path(__file__).parent.parent / 'sql/common_name_prices-0001.sql').read_text()


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0026_common_name_prices_0001'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql),
    ]
