from django import test
from django.db import models

from inventory import models as inv_models


class SourceItemWideFilterTestCase(test.TransactionTestCase):
    fixtures = ["source.json"]

    def setUp(self):
        pass

    def test_example_source(self):
        qs = inv_models.Source.objects.filter(id="11111111-1111-1111-1111-111111111111")
        self.assertEquals(qs.count(), 1)
        self.assertEquals(qs.first().name, "example source")

    def test_get_wide_filter_a(self):
        obj = inv_models.SourceItem.get_wide_filter(("term1", "term2", "term3"), "name")
        self.assertIsInstance(obj, models.Q)

    def test_get_combined_filter(self):
        search_terms = [
            ('name', ('term1', 'term2')),
            ('unit_size', ('8oz')),
        ]
        obj = inv_models.SourceItem.objects.get_combined_filter(search_terms)
        self.assertIsInstance(obj, models.Q)
