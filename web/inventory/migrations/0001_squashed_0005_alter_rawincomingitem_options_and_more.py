# Generated by Django 4.0.1 on 2022-03-06 03:36

from django.db import migrations, models
import django.db.models.deletion
import scrap.fields.char_field
import scrap.fields.money_field
import uuid


class Migration(migrations.Migration):

    replaces = [
        ('inventory', '0001_initial'),
        ('inventory', '0002_rawincomingitem_rawstate_and_more'),
        ('inventory', '0003_alter_rawstate_options'),
        ('inventory', '0004_alter_rawincomingitem_state'),
        ('inventory', '0005_alter_rawincomingitem_options_and_more')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
                ('abbreviation', models.CharField(blank=True, default='', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='RawState',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', scrap.fields.char_field.CharField(blank=True, default='', help_text='short name of the status', max_length=1024)),
                ('description', scrap.fields.char_field.CharField(blank=True, default='', help_text='Short description of the status', max_length=1024)),
                ('value', models.IntegerField(help_text='incrementing value to help sort progress')),
            ],
        ),
        migrations.AddConstraint(
            model_name='rawstate',
            constraint=models.UniqueConstraint(fields=('value',), name='unique_raw_state_value'),
        ),
        migrations.AlterModelOptions(
            name='rawstate',
            options={'ordering': ('value',)},
        ),
        migrations.CreateModel(
            name='RawIncomingItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('source', scrap.fields.char_field.CharField(blank=True, default='', help_text='source name', max_length=1024)),
                ('department', scrap.fields.char_field.CharField(blank=True, default='', help_text='department name', max_length=1024)),
                ('order_number', scrap.fields.char_field.CharField(blank=True, default='', help_text='possibly unique text - some sources repeat or slightly modify this for back-ordered items', max_length=1024)),
                ('po_text', scrap.fields.char_field.CharField(blank=True, default='', help_text='optional text on the invoice', max_length=1024)),
                ('order_comment', scrap.fields.char_field.CharField(blank=True, default='', help_text='Anything noteworthy about this order', max_length=1024)),
                ('order_date', models.DateField(blank=True, help_text='When the order was placed.', null=True)),
                ('delivery_date', models.DateField(help_text='When did we get the items.  Not when the items were shipped.')),
                ('total_price', scrap.fields.money_field.MoneyField(decimal_places=4, default=0, max_digits=10)),
                ('total_packs', scrap.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('line_item_position', models.PositiveSmallIntegerField(null=True, verbose_name='Position')),
                ('category', scrap.fields.char_field.CharField(blank=True, default='', help_text='meat, dairy, produce, etc.', max_length=1024)),
                ('name', scrap.fields.char_field.CharField(blank=True, default='', max_length=1024)),
                ('ordered_quantity', scrap.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('delivered_quantity', scrap.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('total_weight', scrap.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('pack_quantity', scrap.fields.decimal_field.DecimalField(decimal_places=4, default=0, max_digits=10)),
                ('pack_price', scrap.fields.money_field.MoneyField(decimal_places=4, default=0, max_digits=10)),
                ('pack_tax', scrap.fields.money_field.MoneyField(decimal_places=4, default=0, max_digits=10)),
                ('extended_price', scrap.fields.money_field.MoneyField(decimal_places=4, default=0, max_digits=10)),
                ('item_comment', scrap.fields.char_field.CharField(blank=True, default='', help_text='Anything noteworthy about this item', max_length=1024)),
                ('state', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='raw_items', related_query_name='raw_items', to='inventory.rawstate', to_field='value')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='rawincomingitem',
            options={'ordering': ('delivery_date', 'source', 'line_item_position')},
        ),
    ]