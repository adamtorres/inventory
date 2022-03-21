import collections

from django.db import models


def get_unit(unit_size):
    return unit_size.translate(str.maketrans("1234567890-./#", "              ")).strip()


class GetsManagerMixin:
    def get_possible_unit_counts(self, as_list_of_tuples=False):
        raw_unit_qs = self.values('unit_size').annotate(count=models.Count('id'))
        unit_size_counts = collections.defaultdict(int)
        for raw_unit_count in raw_unit_qs:
            unit = get_unit(raw_unit_count['unit_size'])
            unit_size_counts[unit] += raw_unit_count['count']
        if as_list_of_tuples:
            return [(k, unit_size_counts[k]) for k in sorted(unit_size_counts.keys())]
        return unit_size_counts


class GetsModelMixin:
    def get_possible_unit(self):
        return get_unit(self.unit_size)
