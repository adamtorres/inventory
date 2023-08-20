# Recipe - Common multipliers.
from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models, utils as sc_utils
from scrap.models import fields as sc_fields


class RecipeManager(models.Manager):
    def recipes(self):
        """
        Usable recipes.  Excludes templates
        :return:
        """
        return self.exclude(template=True)

    def templates(self):
        """
        Only templates
        :return:
        """
        return self.filter(template=True)


class Recipe(sc_models.DatedModel):
    # Foreign key to multiple Ingredients
    # Foreign key to multiple RecipeSteps
    name = sc_fields.CharField(blank=False)
    source = sc_fields.CharField(help_text="url if from a site.  Book/page, etc?")
    description = sc_fields.CharField(help_text="General description")
    reason_to_not_make = sc_fields.CharField(help_text="Argument to not make this.  More definitive for filtering")
    star_acceptance = models.IntegerField(null=True, help_text="How well did people like it?")
    star_effort = models.IntegerField(null=True, help_text="How much fun was it to make?")
    common_multipliers = pg_fields.ArrayField(models.IntegerField(), default=list, help_text="")
    # TODO: Baking temp/time, pan placement (does this cookie spread?)
    # TODO: category: cookie, bread, bar, fudge, cake, cupcake, unspecified dessert, entree, etc
    template = models.BooleanField(default=False, help_text="Use this as a template - do not include on normal lists")

    objects = RecipeManager()

    def __str__(self):
        return f"{self.name}, {sc_utils.cutoff(self.description)}"

    def clone(self, include_ingredients=True, include_steps=True, include_comments=False, cleaned_data=None):
        """
        Clone the Recipe object and populate anything from cleaned_data into the new object.

        :param include_ingredients:
        :param include_steps:
        :param include_comments:
        :param cleaned_data: Dict from the submitted form
        :return:
        """
        backup_pk = self.pk
        new_recipe = self
        new_recipe.pk = None
        new_recipe.template = False
        for k in cleaned_data or {}:
            if k in ["pk", "id", "template"]:
                continue
            if hasattr(new_recipe, k):
                setattr(new_recipe, k, cleaned_data[k])
        new_recipe.save()
        # Doing .pk=None seems to bork self.  Fix it so the ingredients, steps, and comments can be copied.
        self = Recipe.objects.get(pk=backup_pk)

        def clone_things(plural_thing_name):
            new_things = []
            for thing in getattr(self, plural_thing_name).all():
                thing.pk = None
                thing.recipe = new_recipe
                new_things.append(thing)
            return new_things

        if include_ingredients:
            new_recipe.ingredients.bulk_create(clone_things("ingredients"))
        if include_steps:
            new_recipe.steps.bulk_create(clone_things("steps"))
        if include_comments:
            new_recipe.comments.bulk_create(clone_things("comments"))
        return new_recipe

    def pinned_comments(self):
        return self.comments.filter(pinned=True).order_by('-created')

    def unpinned_comments(self):
        return self.comments.filter(pinned=False).order_by('-created')
