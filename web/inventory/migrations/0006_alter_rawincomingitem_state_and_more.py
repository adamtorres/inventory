# Generated by Django 4.0.1 on 2022-03-24 19:43

from django.db import migrations, models
import django.db.models.deletion
import inventory.models.raw_state


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_iteminstock_raw_incoming_item_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawincomingitem',
            name='state',
            field=models.ForeignKey(default=inventory.models.raw_state.RawStateManager.initial_state, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate'),
        ),
        migrations.AlterField(
            model_name='rawitem',
            name='common_item_name_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='raw_items', related_query_name='raw_items', to='inventory.commonitemnamegroup'),
        ),
    ]
