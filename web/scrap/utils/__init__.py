import inspect
import sys

from .dates import get_monthly_date_range, last_months, recent_quarters
from .uuid import is_valid_uuid


def get_function_name(frames=1):
    # if frames == 1:
    #     return inspect.currentframe().f_code.co_name
    return sys._getframe(frames).f_code.co_name if hasattr(sys, "_getframe") else None


def list_group(source, fields, group_name=None, sub_group_fields=None, count_fields=None, sum_fields=None, set_fields=None):
    """
    given a list of dict (output of qs.annotate), and fields, will return grouping somehow.
    Expects the source to already be sorted?
    """
    if isinstance(fields, str):
        fields = [fields]

    if isinstance(sub_group_fields, str):
        sub_group_fields = [sub_group_fields]
    if sub_group_fields is None:
        sub_group_fields = []

    if isinstance(count_fields, str):
        count_fields = [count_fields]
    if count_fields is None:
        count_fields = []

    if isinstance(sum_fields, str):
        sum_fields = [sum_fields]
    if sum_fields is None:
        sum_fields = []

    if isinstance(set_fields, str):
        set_fields = [set_fields]
    if set_fields is None:
        set_fields = []

    if not group_name:
        group_name = "groups"

    holding = {f: None for f in fields}
    counts = {f: 0 for f in count_fields}
    sums = {f: 0 for f in sum_fields}
    sets = {f: set() for f in set_fields}
    sub_group_holding = {f: None for f in sub_group_fields}
    sub_group_for_current = []
    results = []
    total_count = 0
    for record in source:
        if any([holding[f] != record[f] for f in fields]):
            if total_count:
                sub_group_holding.update(counts)
                sub_group_holding.update(sums)
                sub_group_holding.update(sets)
                sub_group_for_current.append(sub_group_holding)
                holding[group_name] = sub_group_for_current
                sub_group_for_current = []
                results.append(holding)
            holding = {f: record[f] for f in fields}
            sub_group_holding = {f: record[f] for f in sub_group_fields}
            counts = {f: 0 for f in count_fields}
            sums = {f: 0 for f in sum_fields}
            sets = {f: set() for f in set_fields}
        if any([sub_group_holding[f] != record[f] for f in sub_group_fields]):
            sub_group_holding.update(counts)
            sub_group_holding.update(sums)
            sub_group_holding.update(sets)
            sub_group_for_current.append(sub_group_holding)
            counts = {f: 0 for f in count_fields}
            sums = {f: 0 for f in sum_fields}
            sets = {f: set() for f in set_fields}
            sub_group_holding = {f: record[f] for f in sub_group_fields}
        for f in count_fields:
            if record[f]:
                counts[f] += 1
        for f in sum_fields:
            if record[f]:
                sums[f] += record[f]
        for f in set_fields:
            if record[f]:
                sets[f].update(set(record[f]))
        total_count += 1
    sub_group_holding.update(counts)
    sub_group_holding.update(sums)
    sub_group_holding.update(sets)
    sub_group_for_current.append(sub_group_holding)
    holding[group_name] = sub_group_for_current
    if total_count:
        results.append(holding)
    return results

