# Generated by Django 4.2.16 on 2024-10-13 00:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0028_order_contact_number'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='order',
            options={'ordering': ['expected_date', 'who', 'id']},
        ),
    ]
