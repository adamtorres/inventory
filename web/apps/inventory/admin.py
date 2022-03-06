from django.contrib import admin

from . import models as inv_models


# class ArticleAdmin(admin.ModelAdmin):
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         # qs = qs.prefetch_related('author')
#         qs = qs.select_related('author')
#         return qs


# admin.site.register(inv_models.Article, ArticleAdmin)
admin.site.register(inv_models.Category)
admin.site.register(inv_models.Department)
