# Generated by Django 4.0.1 on 2022-02-03 02:40

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_alter_change_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
            ],
        ),
        migrations.AddField(
            model_name='commonitem',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.category'),
        ),
        migrations.AddField(
            model_name='commonitem',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location'),
        ),
        migrations.AddField(
            model_name='item',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='inventory.location'),
        ),
    ]