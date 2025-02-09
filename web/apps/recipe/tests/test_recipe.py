from django import test
from django.db import models

from recipe import models as rcp_models


class RecipeTestCase(test.TransactionTestCase):
    # fixtures = ["source.json"]

    def setUp(self):
        pass

    def test_recipe_example_just_to_make_sure_this_test_file_works(self):
        self.assertEqual(1, 1)
        self.assertEqual("example source", "example source")
