from django.core.management.base import BaseCommand

from ... import models as inv_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        for sc in inv_models.SearchCriteria.objects.all():
            previous_slug = sc.url_slug
            sc.refresh_url_slug()
            sc.save()
            print(f"Updated {sc.name!r} from {previous_slug!r} to {sc.url_slug!r}.")
        print("done.")
