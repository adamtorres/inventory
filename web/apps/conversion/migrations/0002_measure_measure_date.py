# Generated by Django 4.0.6 on 2022-10-16 00:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='measure',
            name='measure_date',
            field=models.DateField(default=datetime.date(2022, 10, 16), help_text='When the measurement was taken'),
            preserve_default=False,
        ),
    ]
