from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory'

    def ready(self):
        print("InventoryConfig.ready")
        # from django.db import models
        # from . import models as inv_models
        # models.CharField.register_lookup(inv_models.MyStartsWith)
        # models.CharField.register_lookup(inv_models.MyEndsWith)
        # models.TextField.register_lookup(inv_models.MyStartsWith)
        # models.TextField.register_lookup(inv_models.MyEndsWith)
