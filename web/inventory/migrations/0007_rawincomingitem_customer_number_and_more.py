# Generated by Django 4.0.1 on 2022-03-13 22:31

from django.db import migrations
import scrap.models.fields.char_field


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_rawstate_failed'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawincomingitem',
            name='customer_number',
            field=scrap.models.fields.char_field.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='rawincomingitem',
            name='extra_code',
            field=scrap.models.fields.char_field.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='rawincomingitem',
            name='item_code',
            field=scrap.models.fields.char_field.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AddField(
            model_name='rawincomingitem',
            name='unit_size',
            field=scrap.models.fields.char_field.CharField(blank=True, default='', max_length=1024),
        ),
    ]
