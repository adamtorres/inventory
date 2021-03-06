# Generated by Django 4.0.1 on 2022-03-27 22:40

from django.db import migrations, models
import django.db.models.deletion
import inventory.models.raw_state


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_usage_comment_usagegroup_comment_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawincomingitem',
            name='state',
            field=models.ForeignKey(default=inventory.models.raw_state.RawStateManager.initial_state, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate'),
        ),
        migrations.AlterField(
            model_name='usage',
            name='usage_group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='usages', related_query_name='usages', to='inventory.usagegroup'),
        ),
    ]
