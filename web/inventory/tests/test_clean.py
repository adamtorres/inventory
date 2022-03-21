import collections
from django.test import TestCase

from inventory.incoming_actions import clean


class TestClean(TestCase):
    TestData = collections.namedtuple("TestData", ['test', 'args', 'expected'])

    def test_unit_size_validation(self):
        test_data = map(lambda x: self.TestData(*x), [
            ("UNIT_SIZE_COUNT_RE", "12ct", {"value": '12', "unit": "ct"}),
            ("UNIT_SIZE_POUND_RE", "12ct", None),
            ("UNIT_SIZE_COUNT_RE", "7ct", {"value": '7', "unit": "ct"}),
            ("UNIT_SIZE_POUND_RE", "7ct", None),
            ("UNIT_SIZE_COUNT_RE", "12lb", None),
            ("UNIT_SIZE_POUND_RE", "12lb", {"value": '12', "unit": "lb"}),
            ("UNIT_SIZE_COUNT_RE", "42lbs", None),
            ("UNIT_SIZE_POUND_RE", "42lbs", {"value": '42', "unit": "lbs"}),
            ("UNIT_SIZE_COUNT_RE", "7-10#AVG", None),
            ("UNIT_SIZE_POUND_RE", "7-10#AVG", None),
            ("UNIT_SIZE_COUNT_RE", "#10", None),
            ("UNIT_SIZE_POUND_RE", "#10", None),
        ])
        for td in test_data:
            with self.subTest(test=td.test, args=td.args, expected=td.expected):
                result = getattr(clean, td.test).match(td.args)
                if td.expected:
                    self.assertEqual(result.group("value"), td.expected['value'])
                    self.assertEqual(result.group("unit"), td.expected['unit'])
                else:
                    self.assertIsNone(result)
