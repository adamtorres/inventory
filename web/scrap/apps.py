from django.apps import AppConfig


class ScrapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scrap'

    def ready(self):
        # TODO: Figure out why the IntegerField example works but the CharField/Field doesn't.
        # from django.db import models
        # from .models import fields as inv_fields
        # models.Field.register_lookup(inv_fields.MyStartsWith)
        # models.Field.register_lookup(inv_fields.MyEndsWith)
        # models.TextField.register_lookup(inv_fields.MyStartsWith)
        # models.TextField.register_lookup(inv_fields.MyEndsWith)
        # inv_fields.CharField.register_lookup(inv_fields.MyStartsWith)
        # inv_fields.CharField.register_lookup(inv_fields.MyEndsWith)
        # models.IntegerField.register_lookup(inv_fields.AbsoluteValue)
        pass
