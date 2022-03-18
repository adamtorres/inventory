from django.core.management.base import BaseCommand

from inventory import models as inv_models


class Command(BaseCommand):
    help = """
    Show counts per table and some reports
    Example usage:
        python manage.py show_counts
    """

    def handle(self, *args, **options):
        inv_models.console_show_counts()
