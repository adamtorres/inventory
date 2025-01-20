from inventory import models as inv_models


def run():
    item_ids = [
        "675c1d14-0ecc-4e1c-9199-986300e183a5",  # diced peach
        "2fa36793-0e97-4619-8109-08c1f9ae8d31",  # sliced peach
        "3cd2267d-fa72-4b69-8b48-839c90c9b0eb",  # 50# sugar
        "c05372d3-670f-4bf6-862b-fbc23a03fe7f",  # 168ct string cheese
    ]
    items = inv_models.SourceItem.objects.example_items()
    for i in items:
        print(f"item: {i.common_name}, {i.id}")
        print(f"\tdate delivered: {i.delivered_date}, order number: {i.order_number}")
        print(f"\tquantity: initial={i.initial_quantity()} old={i.remaining_quantity} pack={i.remaining_pack_quantity} count={i.remaining_count_quantity}")
        print(f"\tget_remaining_quantity(use_type={i.use_type}): {i.get_remaining_quantity(i.use_type)}")
        print(f"\tper use cost: {i.per_use_cost(2)}")
        print(f"\tcalculated pack cost: {i.calculated_pack_cost(2)}")
        print(f"\tremaining cost: {i.remaining_cost(2)}")

        # !! Function not used?  Added 9/9/22
        # !! Old function.  Was written before the forms to add items to the db was written.
        # i.get_remaining_quantity(_use_type)
        #       use_type.use_type_to_single_word(_use_type)
        #           inventory/common/use_type.py
        #           Converts BP/BU/BC into "pack", "unit", "count".
        #       Uses that single lowercase word to find the property remaining_X_quantity
        #       !! There is no remaining_unit_quantity field.

