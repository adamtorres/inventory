from inventory import models as inv_models


def show_counts(tag):
    print(f"removing data {tag}:")
    inv_models.console_show_counts()
    print()


def run(*args):
    print()
    show_counts("before")
    if 'truncate' in args:
        inv_models.RawIncomingItem.objects.all().delete()
    inv_models.RawIncomingItem.objects.reset_all()
    # inv_models.RawIncomingItem.objects.all().update(state=inv_models.RawState.objects.get_by_action('calculate'))
    inv_models.RawItem.objects.all().delete()
    inv_models.CommonItemName.objects.all().delete()
    inv_models.Category.objects.all().delete()
    inv_models.Source.objects.all().delete()
    inv_models.Department.objects.all().delete()
    show_counts("after")

