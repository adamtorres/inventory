# Generated by Django 4.0.6 on 2023-08-21 03:02

from django.db import migrations
import scrap.models.fields.char_field


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_searchcriteria'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchcriteria',
            name='category',
            field=scrap.models.fields.char_field.CharField(blank=True, default='', help_text='Self-defined category as some vendors seem to randomly assign them', max_length=1024),
        ),
    ]