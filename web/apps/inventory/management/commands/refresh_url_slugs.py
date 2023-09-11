from django.core.management.base import BaseCommand
from django.db import models

from ... import models as inv_models


class Command(BaseCommand):
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--overwrite',
            action='store_true',
            dest='overwrite',
            help="Overwrite existing url_slug values instead of only adding where missing.",
            default=False,
        )

    def handle(self, *args, **options):
        if options["overwrite"]:
            qs = inv_models.SearchCriteria.objects.all()
        else:
            qs = inv_models.SearchCriteria.objects.filter(models.Q(url_slug__isnull=True)|models.Q(url_slug=""))
        for sc in qs:
            previous_slug = sc.url_slug
            sc.refresh_url_slug()
            sc.save()
            print(f"Updated {sc.name!r} from {previous_slug!r} to {sc.url_slug!r}.")
        print("done.")
