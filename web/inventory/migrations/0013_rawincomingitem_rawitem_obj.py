# Generated by Django 4.0.1 on 2022-03-15 22:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_rawincomingitem_source_obj'),
    ]

    operations = [
        migrations.AddField(
            model_name='rawincomingitem',
            name='rawitem_obj',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.rawitem'),
        ),
    ]