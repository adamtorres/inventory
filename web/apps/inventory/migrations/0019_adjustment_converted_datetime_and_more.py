# Generated by Django 4.0.2 on 2022-02-08 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_remove_itemchange_applied_change_applied_datetime_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='adjustment',
            name='converted_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='usage',
            name='converted_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
