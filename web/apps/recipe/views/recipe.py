from django import urls
from django.views import generic

from recipe import models as rcp_models


class RecipeCreateView(generic.CreateView):
    model = rcp_models.Recipe
    fields = [
        'name', 'source', 'description', 'reason_to_not_make', 'star_acceptance', 'star_effort', 'common_multipliers']

    def get_success_url(self):
        return urls.reverse('recipe:recipe_detail', args=(self.object.id,))


class RecipeDetailView(generic.DetailView):
    queryset = rcp_models.Recipe.objects.all()


class RecipeListView(generic.ListView):
    queryset = rcp_models.Recipe.objects.all()


class RecipeUpdateView(generic.UpdateView):
    model = rcp_models.Recipe

    def get_success_url(self):
        return urls.reverse('recipe:recipe_detail', args=(self.object.id,))
