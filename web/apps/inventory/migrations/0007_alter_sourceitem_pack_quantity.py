# Generated by Django 4.1 on 2022-08-17 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_sourceitem_pack_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sourceitem',
            name='pack_quantity',
            field=models.IntegerField(default=1, help_text='For a pack of 6 #10 cans, this would be 6.'),
        ),
    ]