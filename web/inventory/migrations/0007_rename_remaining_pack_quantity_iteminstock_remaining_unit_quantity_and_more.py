# Generated by Django 4.0.1 on 2022-03-26 22:08

from django.db import migrations, models
import django.db.models.deletion
import inventory.models.raw_state


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_rawincomingitem_state_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='iteminstock',
            old_name='remaining_pack_quantity',
            new_name='remaining_unit_quantity',
        ),
        migrations.AlterField(
            model_name='rawincomingitem',
            name='state',
            field=models.ForeignKey(default=inventory.models.raw_state.RawStateManager.initial_state, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate'),
        ),
    ]
