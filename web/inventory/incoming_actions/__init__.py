import json

from .. import models as inv_models
from .calculate import _do_calculate
from .clean import _do_clean
from .create import _do_create
from .import_item import _do_import


def update_item_state(list_of_items, fields_to_update, batch_size=100):
    if list_of_items:
        return inv_models.RawIncomingItem.objects.bulk_update(
            list_of_items, fields_to_update, batch_size=batch_size)
    return 0


def do_all_actions(batch_size=1):
    do_clean(batch_size=batch_size)
    do_calculate(batch_size=batch_size)
    do_create(batch_size=batch_size)
    do_import(batch_size=batch_size)


def do_calculate(batch_size=1):
    items_to_update, fields_to_update = _do_calculate(batch_size=batch_size)
    update_item_state(items_to_update, fields_to_update, batch_size=batch_size)


def do_clean(batch_size=1):
    items_to_update, fields_to_update = _do_clean(batch_size=batch_size)
    update_item_state(items_to_update, fields_to_update, batch_size=batch_size)


def do_create(batch_size=1):
    items_to_update, fields_to_update = _do_create(batch_size=batch_size)
    update_item_state(items_to_update, fields_to_update, batch_size=batch_size)


def do_import(batch_size=1):
    items_to_update, fields_to_update = _do_import(batch_size=batch_size)
    update_item_state(items_to_update, fields_to_update, batch_size=batch_size)


def report_on_failures():
    qs = inv_models.RawIncomingItem.objects.failed()
    failure_reasons = {}
    for item in qs:
        item_failure_reasons = json.loads(item.failure_reasons)
        for failure in item_failure_reasons:
            if failure['failure'] not in failure_reasons:
                print(failure)
                failure_reasons[failure['failure']] = {'count': 0, 'items': set(), 'fields': failure['fields']}
            failure_reasons[failure['failure']]['count'] += 1
            failure_reasons[failure['failure']]['items'].add(item.id)
    for reason, reason_data in failure_reasons.items():
        print(f"{reason_data['count']} = {reason}")
        if reason == 'empty or None':
            continue
        qs = inv_models.RawIncomingItem.objects.filter(id__in=reason_data['items'])
        for i, item in enumerate(qs):
            item_failure_reasons = json.loads(item.failure_reasons)
            line = ""
            for item_reason in item_failure_reasons:
                if item_reason['failure'] != reason:
                    continue
                if 'difference' in item_reason:
                    line += f"difference = {item_reason.get('difference', 'nope')}, "
            line += ", ".join([f"{field} = {getattr(item, field)!r}" for field in sorted(reason_data['fields'])])
            print(line)
