from django.contrib import admin

from . import models as rcp_models


admin.site.register(rcp_models.Item)
admin.site.register(rcp_models.Recipe)
admin.site.register(rcp_models.RecipeComment)
admin.site.register(rcp_models.RecipeIngredient)
admin.site.register(rcp_models.RecipeStep)
