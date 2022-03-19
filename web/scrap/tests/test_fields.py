from django.db import models
from django.test import TestCase

from ..models import fields as sc_fields


class ScrapFieldsTestCase(TestCase):
    """
    These fields get used directly by migrations.  If some property of them gets changed, then the database created by
    those migrations will be different.  These tests are just to remind me of that in case some issue crops up because
    of a change.
    """
    migration_error_message = "will earlier migrations break?"

    def test_money_field(self):
        x = sc_fields.MoneyField()
        self.assertIsInstance(x, models.DecimalField)
        self.assertEqual(x.max_digits, 10, msg=self.migration_error_message)
        self.assertEqual(x.decimal_places, 4, msg=self.migration_error_message)
        self.assertFalse(x.null, msg=self.migration_error_message)
        self.assertFalse(x.blank, msg=self.migration_error_message)
        self.assertEqual(x.default, 0, msg=self.migration_error_message)

    def test_decimal_field(self):
        x = sc_fields.DecimalField()
        self.assertIsInstance(x, models.DecimalField)
        self.assertEqual(x.max_digits, 10, msg=self.migration_error_message)
        self.assertEqual(x.decimal_places, 4, msg=self.migration_error_message)
        self.assertFalse(x.null, msg=self.migration_error_message)
        self.assertFalse(x.blank, msg=self.migration_error_message)
        self.assertEqual(x.default, 0, msg=self.migration_error_message)

    def test_char_field(self):
        x = sc_fields.CharField()
        self.assertIsInstance(x, models.CharField)
        self.assertEqual(x.max_length, 1024, msg=self.migration_error_message)
        self.assertFalse(x.null, msg=self.migration_error_message)
        self.assertTrue(x.blank, msg=self.migration_error_message)
        self.assertEqual(x.default, "", msg=self.migration_error_message)
