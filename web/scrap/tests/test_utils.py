from django.test import TestCase

from .. import utils as sc_utils


class ScrapUtilsTestCase(TestCase):

    def test_get_function_name_one_level(self):
        func_name = "test_get_function_name_one_level"
        inside_test_func = sc_utils.get_function_name()
        self.assertEqual(inside_test_func, func_name)

        for i in ["one"]:
            inside_loop = sc_utils.get_function_name()
            self.assertEqual(inside_loop, func_name)
