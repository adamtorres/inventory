# Generated by Django 4.0.6 on 2022-09-19 04:00

from django.db import migrations
import scrap.models.fields.money_field


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0010_remove_order_item_pack_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='material_cost_per_item',
            field=scrap.models.fields.money_field.MoneyField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='itempack',
            name='material_cost_per_pack',
            field=scrap.models.fields.money_field.MoneyField(blank=True, decimal_places=4, default=0, max_digits=10, null=True),
        ),
    ]
