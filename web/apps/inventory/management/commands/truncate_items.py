from django.core.management.base import BaseCommand

from ... import models as inv_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("Deleting SourceItems...")
        inv_models.SourceItem.objects.all().delete()
        print("Deleting CommonNames...")
        inv_models.CommonName.objects.all().delete()
        print("done.")
