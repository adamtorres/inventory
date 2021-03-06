# Generated by Django 4.0.1 on 2022-03-24 04:11

from django.db import migrations, models
import django.db.models.deletion
import inventory.models.raw_state
import scrap.models.fields.decimal_field
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_alter_rawincomingitem_pack_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rawincomingitem',
            name='rawitem_obj',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='raw_incoming_items', related_query_name='raw_incoming_items', to='inventory.rawitem'),
        ),
        migrations.AlterField(
            model_name='rawincomingitem',
            name='state',
            field=models.ForeignKey(default=inventory.models.raw_state.RawStateManager.initial_state, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate'),
        ),
        migrations.CreateModel(
            name='ItemInStock',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('original_pack_quantity', scrap.models.fields.decimal_field.DecimalField(decimal_places=4, default=0, help_text='delivered_quantity * pack_quantity', max_digits=10)),
                ('remaining_pack_quantity', scrap.models.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('raw_incoming_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='in_stock', related_query_name='in_stock', to='inventory.rawincomingitem')),
            ],
            options={
                'ordering': ('raw_incoming_item__rawitem_obj__source__name', 'raw_incoming_item__rawitem_obj__common_item_name_group__name__name', 'raw_incoming_item__delivery_date', 'raw_incoming_item__created'),
            },
        ),
    ]
