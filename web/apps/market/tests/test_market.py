from django import test
from django.db import models

from market import models as mkt_models


class MarketTestCase(test.TransactionTestCase):
    # fixtures = ["source.json"]

    def setUp(self):
        pass

    def test_market_example_just_to_make_sure_this_test_file_works(self):
        self.assertEqual(1, 1)
        self.assertEqual("example source", "example source")
