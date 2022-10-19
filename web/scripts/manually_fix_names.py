from django.db import models, transaction
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from conversion import models as con_models
from inventory import models as inv_models


def get_queryset(model, cryptic_name_filter, missing_verbose_name=False, missing_common_name=False):
    if isinstance(cryptic_name_filter, list):
        cryptic_name_filter = '.*'.join(cryptic_name_filter)
    cryptic_name_filter = f".*{cryptic_name_filter}.*"
    qs = model.objects.filter(cryptic_name__iregex=cryptic_name_filter)
    if missing_verbose_name:
        qs = qs.filter(verbose_name="")
    if missing_common_name:
        qs = qs.filter(common_name="")
    return qs


def get_measure_queryset(cryptic_name_filter, missing_verbose_name=False, missing_common_name=False):
    return get_queryset(
        con_models.Measure, cryptic_name_filter, missing_verbose_name=missing_verbose_name,
        missing_common_name=missing_common_name)


def get_source_item_queryset(cryptic_name_filter, missing_verbose_name=False, missing_common_name=False):
    return get_queryset(
        inv_models.SourceItem, cryptic_name_filter, missing_verbose_name=missing_verbose_name,
        missing_common_name=missing_common_name)


def find_them(cryptic_name_filter):
    print(f"\nFinding objects by cryptic_name looking for {cryptic_name_filter!r}")
    for i in get_source_item_queryset(cryptic_name_filter).values('cryptic_name', 'verbose_name', 'common_name'):
        print(f"SourceItem: c({i['cryptic_name']}) v({i['verbose_name']}) com({i['common_name']})")
    for i in get_measure_queryset(cryptic_name_filter).values('cryptic_name', 'verbose_name', 'common_name'):
        print(f"Measure: c({i['cryptic_name']}) v({i['verbose_name']}) com({i['common_name']})")


def fix_them(cryptic_name_filter, verbose_name=None, common_name=None, dry_run=True):
    print(f"\nFixing objects by cryptic_name__icontains={cryptic_name_filter!r}")
    if verbose_name is None:
        print("\tverbose_name unchanged")
    elif verbose_name == 'COPY':
        print("\tverbose_name set to cryptic_name if empty")
    else:
        print(f"\tverbose_name = {verbose_name!r}")
    if common_name is None:
        print("\tcommon_name unchanged")
    else:
        print(f"\tcommon_name = {common_name!r}")

    con_updated_verbose, con_updated_common = 0, 0
    inv_updated_verbose, inv_updated_common = 0, 0
    if verbose_name == "COPY":
        verbose_name = models.F('cryptic_name')
    try:
        with transaction.atomic():
            # This dry_run is ugly but I could not get manual rollbacks to work.  Will try again later.
            if verbose_name:
                inv_verbose_name_qs = get_source_item_queryset(cryptic_name_filter, missing_verbose_name=True)
                inv_updated_verbose = inv_verbose_name_qs.update(verbose_name=verbose_name)
                con_verbose_name_qs = get_measure_queryset(cryptic_name_filter, missing_verbose_name=True)
                con_updated_verbose = con_verbose_name_qs.update(verbose_name=verbose_name)
            if common_name:
                inv_common_name_qs = get_source_item_queryset(cryptic_name_filter, missing_common_name=True)
                inv_updated_common = inv_common_name_qs.update(common_name=common_name)
                con_common_name_qs = get_measure_queryset(cryptic_name_filter, missing_common_name=True)
                con_updated_common = con_common_name_qs.update(common_name=common_name)
            if dry_run:
                print("Dry run.  Rolling back.")
                raise ValueError("Dry Run")
    except ValueError as ex:
        if "Dry Run" not in str(ex):
            raise
    print(f"Updated SourceItem {inv_updated_verbose} verbose names, {inv_updated_common} common names")
    print(f"Updated Measure {con_updated_verbose} verbose names, {con_updated_common} common names")


def run():
    cryptic_name_filter = ["mayonnaise",]
    common_name = "Mayonnaise"
    with monkey_patch_cursordebugwrapper(print_sql=False, confprefix="SHELL_PLUS", print_sql_location=False):
        find_them(cryptic_name_filter)
        fix_them(cryptic_name_filter, verbose_name="COPY", common_name=common_name, dry_run=True)
        find_them(cryptic_name_filter)
