from django.db import models
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper


from inventory import models as inv_models


def selected_item_report():
    common_item_names = [
        "low fat milk cartons",
        "low fat chocolate milk cartons",
        "chocolate pudding",
        "lemon pudding",
        "nonstick spray",
        "butter",
        "margarine",
        "margarine tubs",
        "cool whip",
        "sour cream",
        "cream cheese",
        "flour",
    ]
    selected_item_filter = models.Q(rawitem_obj__common_item_name_group__name__name__in=common_item_names)
    inv_models.RawIncomingItem.reports.console_routinely_ordered_items(
        months=12, selected_item_filter=selected_item_filter)


def run():
    with monkey_patch_cursordebugwrapper(print_sql=True, confprefix="SHELL_PLUS", print_sql_location=False):
        selected_item_report()
