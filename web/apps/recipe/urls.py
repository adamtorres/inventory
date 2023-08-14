from django import urls

from . import views as r_views


app_name = "recipe"

urlpatterns = [
    urls.path("items/", r_views.ItemListView.as_view(), name="item_list"),
    urls.path("item/<uuid:pk>", r_views.ItemDetailView.as_view(), name="item_detail"),
    urls.path("item/new", r_views.ItemCreateView.as_view(), name="item_create"),
    urls.path("item/<uuid:pk>/edit", r_views.ItemUpdateView.as_view(), name="item_update"),

    urls.path("recipes/", r_views.RecipeListView.as_view(), name="recipe_list"),
    urls.path("recipe/<uuid:pk>", r_views.RecipeDetailView.as_view(), name="recipe_detail"),
    urls.path("recipe/new", r_views.RecipeCreateView.as_view(), name="recipe_create"),
    urls.path("recipe/<uuid:pk>/edit", r_views.RecipeUpdateView.as_view(), name="recipe_update"),
    urls.path("recipe/<uuid:pk>/comments", r_views.RecipeCommentUpdateView.as_view(), name="recipe_comment_update"),
    urls.path(
        "recipe/<uuid:pk>/ingredients", r_views.RecipeIngredientUpdateView.as_view(), name="recipe_ingredient_update"),
    urls.path("recipe/<uuid:pk>/steps", r_views.RecipeStepUpdateView.as_view(), name="recipe_step_update"),
]
