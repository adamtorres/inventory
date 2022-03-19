from django.db import models
from django.db.models.lookups import PatternLookup


class MyEndsWith(PatternLookup):
    lookup_name = 'ewhello'
    param_pattern = '%%%s'


class MyStartsWith(PatternLookup):
    lookup_name = 'swhello'
    param_pattern = '%s%%'


class AbsoluteValue(models.Transform):
    lookup_name = 'abs'
    function = 'ABS'
