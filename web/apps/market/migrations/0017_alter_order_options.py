# Generated by Django 4.0.6 on 2022-09-19 04:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0016_alter_order_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['-date_ordered', 'who', 'id']},
        ),
    ]
