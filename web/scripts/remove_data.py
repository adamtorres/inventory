from inventory import models as inv_models


def show_counts(tag):
    print(f"removing data {tag}:")
    print(":RawIncomingItem by state")
    inv_models.RawIncomingItem.reports.console_group_by_current_state()
    print(f":RawItem = {inv_models.RawItem.objects.count()}")
    print(f":CommonItemName = {inv_models.CommonItemName.objects.count()}")
    print(f":Categories = {inv_models.Category.objects.count()}")
    print(f":Source = {inv_models.Source.objects.count()}")
    print(f":Department = {inv_models.Department.objects.count()}")
    print()


def run():
    print()
    show_counts("before")
    inv_models.RawIncomingItem.objects.reset_all()
    # inv_models.RawIncomingItem.objects.all().update(state=inv_models.RawState.objects.get_by_action('calculate'))
    inv_models.RawItem.objects.all().delete()
    inv_models.CommonItemName.objects.all().delete()
    inv_models.Category.objects.all().delete()
    inv_models.Source.objects.all().delete()
    inv_models.Department.objects.all().delete()
    show_counts("after")

