# Generated by Django 4.0.6 on 2022-09-16 04:51

from django.db import migrations, models
import market.models.order


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0004_alter_order_date_ordered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='date_ordered',
            field=models.DateField(default=market.models.order.today),
        ),
    ]
