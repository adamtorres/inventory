from django import urls

from . import views as r_views


app_name = "recipe"

urlpatterns = [
    urls.path("recipes/", r_views.RecipeListView.as_view(), name="recipe_list"),
    urls.path("recipe/<uuid:pk>", r_views.RecipeDetailView.as_view(), name="recipe_detail"),
    urls.path("recipe/new", r_views.RecipeCreateView.as_view(), name="recipe_create"),
    urls.path("recipe/<uuid:pk>/edit", r_views.RecipeUpdateView.as_view(), name="recipe_update"),
    urls.path("recipe/<uuid:pk>/comments", r_views.RecipeCommentUpdateView.as_view(), name="recipe_comment_update"),
    urls.path("recipe/<uuid:pk>/steps", r_views.RecipeStepUpdateView.as_view(), name="recipe_step_update"),
]
