# Generated by Django 4.0.6 on 2023-08-16 05:14

from django.db import migrations, models
import scrap.models.fields.char_field
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0018_vw_orders_entered_today_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchCriteria',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', scrap.models.fields.char_field.CharField(blank=True, default='', help_text='hopefully unique name of this search', max_length=1024)),
                ('description', scrap.models.fields.char_field.CharField(blank=True, default='', max_length=1024)),
                ('criteria', models.JSONField(default=dict)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
    ]
