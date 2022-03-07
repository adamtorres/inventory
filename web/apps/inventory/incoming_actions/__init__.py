from inventory import models as inv_models
from .calculate import _do_calculate
from .clean import _do_clean
from .create import _do_create
from .import_item import _do_import


def update_item_state(list_of_items, fields_to_update):
    return inv_models.RawIncomingItem.objects.bulk_update(
        list_of_items, fields_to_update, batch_size=100)


def do_all_actions(batch_size=1):
    do_clean(batch_size=batch_size)
    do_calculate()
    do_create()
    do_import()


def do_calculate():
    items_to_update, fields_to_update = _do_calculate()
    update_item_state(items_to_update, fields_to_update)


def do_clean(batch_size=1):
    items_to_update, fields_to_update = _do_clean(batch_size=batch_size)
    update_item_state(items_to_update, fields_to_update)


def do_create():
    items_to_update, fields_to_update = _do_create()
    update_item_state(items_to_update, fields_to_update)


def do_import():
    items_to_update, fields_to_update = _do_import()
    update_item_state(items_to_update, fields_to_update)
