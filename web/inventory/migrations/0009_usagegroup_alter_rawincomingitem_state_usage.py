# Generated by Django 4.0.1 on 2022-03-27 21:20

from django.db import migrations, models
import django.db.models.deletion
import inventory.models.raw_state
import scrap.models.fields.char_field
import scrap.models.fields.decimal_field
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_rename_original_pack_quantity_iteminstock_original_unit_quantity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsageGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('description', scrap.models.fields.char_field.CharField(blank=True, default='', max_length=1024)),
                ('when', models.DateField(help_text='when the described activity took place')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='rawincomingitem',
            name='state',
            field=models.ForeignKey(default=inventory.models.raw_state.RawStateManager.initial_state, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate'),
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('used_quantity', scrap.models.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('item_in_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.iteminstock')),
                ('usage_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.usagegroup')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]