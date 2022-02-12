# Generated by Django 4.0.1 on 2022-02-12 03:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incoming', '0016_alter_incomingitemgroup_source'),
    ]

    operations = [
        migrations.AddField(
            model_name='incomingitemgroup',
            name='total_packs',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='incomingitemgroup',
            name='total_price',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
    ]
