from .. import models as inv_models


def _do_import(batch_size=1):
    """
    step 5
    """
    qs = inv_models.RawIncomingItem.objects.ready_to_import()
    if batch_size > 0:
        qs = qs[:batch_size]
    print(f"do_import found {qs.count()} records to import.")
    items_to_update = []
    in_stock_items_to_create = []
    fields_to_update = {'state'}
    for i, item in enumerate(qs):
        qty = item.delivered_quantity * item.pack_quantity
        in_stock_items_to_create.append(
            inv_models.ItemInStock(raw_incoming_item=item, original_unit_quantity=qty, remaining_unit_quantity=qty))
        item.state = item.state.next_state
        items_to_update.append(item)
        # TODO: create the Item objects.
    if in_stock_items_to_create:
        print(f"do_import:Creating {len(in_stock_items_to_create)} InStockItems.")
        inv_models.ItemInStock.objects.bulk_create(in_stock_items_to_create)
    return items_to_update, fields_to_update
