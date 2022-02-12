from django.apps import AppConfig
from django.db.models.signals import post_save

from .signals import recalculate_incoming_item_group


class IncomingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'incoming'

    def ready(self):
        IncomingItem = self.get_model('IncomingItem')
        post_save.connect(recalculate_incoming_item_group, sender=IncomingItem)
