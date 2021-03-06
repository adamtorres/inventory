# Generated by Django 4.0.1 on 2022-03-28 04:59

from django.db import migrations, models
import django.db.models.deletion
import inventory.models.raw_state
import scrap.models.fields.money_field


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0014_alter_usage_options_alter_usagegroup_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='iteminstock',
            name='unit_price',
            field=scrap.models.fields.money_field.MoneyField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='rawincomingitem',
            name='state',
            field=models.ForeignKey(default=inventory.models.raw_state.RawStateManager.initial_state, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate'),
        ),
    ]
