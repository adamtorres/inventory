from django.core.management.base import BaseCommand
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from ... import models as inv_models


class Command(BaseCommand):
    def handle(self, *args, **options):
        with monkey_patch_cursordebugwrapper(print_sql=False, confprefix="SHELL_PLUS", print_sql_location=False):
            # self.reset_verbose_names()
            self.actual_handle(*args, **options)

    def actual_handle(self, *args, **options):
        cn_with_vn = inv_models.CommonName.objects.exclude(verbose_name="").values_list('cryptic_name', flat=True)
        print(f"common names with verbose name: {len(cn_with_vn)}")

        print(f"distinct cryptic names on items: {len(inv_models.SourceItem.objects.cryptic_names())}")
        print(f"distinct verbose names on items: {len(inv_models.SourceItem.objects.verbose_names())}")
        mvn_qs = inv_models.SourceItem.objects.missing_verbose_name().filter(cryptic_name__in=cn_with_vn)
        print(f"distinct cryptic names missing verbose name: {len(mvn_qs)}")
        matches = 0

        for cn in mvn_qs:
            cn_qs = inv_models.CommonName.objects.filter(cryptic_name=cn['cryptic_name']).exclude(verbose_name="")
            if len(cn_qs) == 0:
                print(f"No matches for cryptic name: {cn['cryptic_name']!r}")
            else:
                matches += 1
                print(f"Cryptic name: {cn['cryptic_name']!r} matches {cn_qs}")
                if len(cn_qs) == 1:
                    # Single match.  Just apply it
                    vn = cn_qs.first().verbose_name
                    updated_record_count = inv_models.SourceItem.objects.filter(verbose_name="", **cn).update(verbose_name=vn)
                    print(f"\tUpdated {updated_record_count} records.")
                else:
                    # multiple matches
                    print("\tMultiple matches")
                if matches > 10:
                    break
        print("done.")

    def reset_verbose_names(self):
        reset_count = inv_models.SourceItem.objects.exclude(verbose_name="").update(verbose_name="")
        print(f"Reset {reset_count} records.")
