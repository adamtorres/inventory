from django.core.management.base import BaseCommand

from ... import models as inv_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        # inv_models.SourceItem.objects.all().delete()
        inv_models.CommonName.objects.all().delete()
        print("done.")
