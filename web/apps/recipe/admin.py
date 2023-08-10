from django.contrib import admin

from . import models as rcp_models


admin.site.register(rcp_models.Recipe)
