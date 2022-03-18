from .category import Category
from .common_item_name import CommonItemName, CommonItemNameGroup
from .department import Department
from .raw_incoming_item import RawIncomingItem
from .raw_item import RawItem
from .raw_state import RawState
from .source import Source


def console_show_counts():
    print()
    print(f":RawIncomingItem = {RawIncomingItem.objects.count()}")
    print(f":RawItem = {RawItem.objects.count()}")
    print(f":CommonItemNameGroup = {CommonItemNameGroup.objects.count()}")
    print(f":CommonItemName = {CommonItemName.objects.count()}")
    print(f":Categories = {Category.objects.count()}")
    print(f":Source = {Source.objects.count()}")
    print(f":Department = {Department.objects.count()}")
    print("\n:reports:")
    print(":RawIncomingItem by state")
    RawIncomingItem.reports.console_group_by_current_state()
