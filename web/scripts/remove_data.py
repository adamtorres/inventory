from inventory import models as inv_models


def show_counts(tag):
    print(f"removing data {tag}:")
    inv_models.console_show_counts()
    print()


def run(*args):
    print()
    show_counts("before")
    inv_models.Usage.objects.all().delete()
    inv_models.UsageGroup.objects.all().delete()
    inv_models.ItemInStock.objects.all().delete()
    inv_models.Item.objects.all().delete()
    if 'truncate' in args:
        inv_models.RawIncomingItem.objects.all().delete()
    inv_models.RawIncomingItem.objects.reset_all()
    inv_models.RawItem.objects.all().delete()
    inv_models.CommonItemName.objects.all().delete()
    inv_models.CommonItemNameGroup.objects.all().delete()
    inv_models.Category.objects.all().delete()
    inv_models.Source.objects.all().delete()
    inv_models.Department.objects.all().delete()
    show_counts("after")

