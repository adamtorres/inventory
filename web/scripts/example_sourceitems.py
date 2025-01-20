from inventory import models as inv_models


def run():
    example_item_qs = inv_models.SourceItem.objects.example_items()
    print(f"Got {example_item_qs.count()} items.")
    for item in example_item_qs:
        print(f"{item} / {item.common_name}")
