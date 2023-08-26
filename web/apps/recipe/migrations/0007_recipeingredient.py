# Generated by Django 4.0.6 on 2023-08-14 17:37

from django.db import migrations, models
import django.db.models.deletion
import scrap.models.fields.char_field
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('recipe', '0006_alter_item_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('ingredient_number', models.IntegerField(default=0)),
                ('optional', models.BooleanField(default=False, help_text='Can this ingredient be skipped')),
                ('pre_preparation', scrap.models.fields.char_field.CharField(blank=True, default='', help_text='Preprep for this ingredient: chopped/melted/room temp/etc', max_length=1024)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', related_query_name='ingredients', to='recipe.item')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ingredients', related_query_name='ingredients', to='recipe.recipe')),
            ],
            options={
                'ordering': ['recipe', 'ingredient_number'],
            },
        ),
    ]