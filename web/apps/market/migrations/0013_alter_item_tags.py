# Generated by Django 4.0.6 on 2022-09-19 04:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0012_alter_item_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, related_name='items', related_query_name='items', to='market.tag'),
        ),
    ]