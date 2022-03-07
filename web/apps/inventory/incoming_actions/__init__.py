from inventory import models as inv_models
from .analyze import _do_analyze
from .calculate import _do_calculate
from .clean import _do_clean
from .create import _do_create
from .import_item import _do_import


def update_item_state(list_of_items):
    return inv_models.RawIncomingItem.objects.bulk_update(list_of_items, ('state', ), batch_size=100)


def do_analyze():
    items_to_update = _do_analyze()
    update_item_state(items_to_update)


def do_calculate():
    items_to_update = _do_calculate()
    update_item_state(items_to_update)


def do_clean():
    items_to_update = _do_clean()
    update_item_state(items_to_update)


def do_create():
    items_to_update = _do_create()
    update_item_state(items_to_update)


def do_import():
    items_to_update = _do_import()
    update_item_state(items_to_update)
