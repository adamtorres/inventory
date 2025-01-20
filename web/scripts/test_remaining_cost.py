from inventory import models as inv_models


from scrap import utils as sc_utils


def run():
    item_ids = [
        "675c1d14-0ecc-4e1c-9199-986300e183a5",  # diced peach
        "2fa36793-0e97-4619-8109-08c1f9ae8d31",  # sliced peach
        "3cd2267d-fa72-4b69-8b48-839c90c9b0eb",  # 50# sugar
        "c05372d3-670f-4bf6-862b-fbc23a03fe7f",  # 168ct string cheese
    ]
    items = inv_models.SourceItem.objects.example_items()
    headers = [
        "date deli", "order num", "init qty", "old", "pack", "count", "GRQ(?)", "puc", "calc pack cost", "rem cost",
        "name"]
    col_widths = [10, 12, 8, 3, 4, 5, 7, 6, 14, 8, 30]
    col_align = [">", ">", ">", ">", ">", ">", ">", ">", ">", ">", "<"]
    print("  ".join(f"{h:{col_align[idx]}{col_widths[idx]}}" for idx, h in enumerate(headers)))
    for i in items:
        data = [
            str(i.delivered_date), i.order_number, i.initial_quantity(), i.remaining_quantity,  i.remaining_pack_quantity,
            i.remaining_count_quantity, f"{i.use_type}={i.get_remaining_quantity(i.use_type)}", i.per_use_cost(2),
            i.calculated_pack_cost(2), i.remaining_cost(2), sc_utils.cutoff(i.common_name, 30)
        ]
        print("  ".join(f"{d:{col_align[idx]}{col_widths[idx]}}" for idx, d in enumerate(data)))
        # !! Function not used?  Added 9/9/22
        # !! Old function.  Was written before the forms to add items to the db was written.
        # i.get_remaining_quantity(_use_type)
        #       use_type.use_type_to_single_word(_use_type)
        #           inventory/common/use_type.py
        #           Converts BP/BU/BC into "pack", "unit", "count".
        #       Uses that single lowercase word to find the property remaining_X_quantity
        #       !! There is no remaining_unit_quantity field.

