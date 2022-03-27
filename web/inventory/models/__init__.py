from .category import Category
from .common_item_name import CommonItemName, CommonItemNameGroup
from .department import Department
from .item import Item
from .item_in_stock import ItemInStock
from .raw_incoming_item import RawIncomingItem
from .raw_item import RawItem
from .raw_state import RawState
from .source import Source
from .usage import Usage, UsageGroup


def console_show_counts():
    print()
    counts = get_model_counts()
    for model_name in sorted(counts.keys()):
        print(f":{model_name} = {counts[model_name]}")
    print("\n:reports:")
    print(":RawIncomingItem by state")
    RawIncomingItem.reports.console_group_by_current_state()


def get_model_counts():
    return {
        "UsageGroup": UsageGroup.objects.count(),
        "Usage": Usage.objects.count(),
        "Item": Item.objects.count(),
        "ItemInStock": ItemInStock.objects.count(),
        "RawIncomingItem": RawIncomingItem.objects.count(),
        "RawItem": RawItem.objects.count(),
        "CommonItemNameGroup": CommonItemNameGroup.objects.count(),
        "CommonItemName": CommonItemName.objects.count(),
        "Category": Category.objects.count(),
        "Source": Source.objects.count(),
        "Department": Department.objects.count(),
    }