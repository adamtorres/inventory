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
            ('unit_size', ('8oz', )),
        ]
        combined_filter = inv_models.SourceItem.objects.get_combined_filter(search_terms)
        self.validate_combined_filter(combined_filter, search_terms)

    def validate_combined_filter(self, combined_filter, search_terms):
        # <Q: (
        #   AND: (
        #       OR:
        #         (AND: ('cryptic_name__icontains', 'term1'), ('cryptic_name__icontains', 'term2')),
        #         (AND: ('verbose_name__icontains', 'term1'), ('verbose_name__icontains', 'term2')),
        #         (AND: ('common_name__icontains', 'term1'), ('common_name__icontains', 'term2'))
        #        ),
        #       ('unit_size__icontains', '8oz'))>
        self.assertIsInstance(combined_filter, models.Q)
        self.assertEquals(len(combined_filter.children), len(search_terms))
        self.assertEquals(combined_filter.connector, 'AND')

        name_filter = combined_filter.children[0]
        self.assertIsInstance(name_filter, models.Q)
        self.assertEquals(len(name_filter.children), len(inv_models.SourceItem.wide_filter_fields['name']))
        self.assertEquals(name_filter.connector, 'OR')

        # Fancy way to validate the correct Q/tuple values are in the name filter.  Because lists are used, things
        # should always be in a predictable order.
        # multiple database fields and multiple terms makes this a bit nested.
        for name_filter_i, db_field_name in enumerate(inv_models.SourceItem.wide_filter_fields['name']):
            name_field_filter = name_filter.children[name_filter_i]
            self.assertEquals(len(name_field_filter.children), len(search_terms[0][1]))  # ('term1', 'term2')
            self.assertIsInstance(name_field_filter, models.Q)
            self.assertEquals(name_field_filter.connector, 'AND')
            for i, name_field_filter_tuple in enumerate(name_field_filter.children):
                with self.subTest(db_field_name=db_field_name, name_field_filter_tuple=name_field_filter_tuple, i=i):
                    self.assertIsInstance(name_field_filter_tuple, tuple)
                    self.assertEquals(name_field_filter_tuple[0], f"{db_field_name}__icontains")
                    self.assertEquals(name_field_filter_tuple[1], search_terms[0][1][i])

        # unit_size is simple as there's only one term and one field tested.
        unit_size_filter = combined_filter.children[1]
        self.assertIsInstance(unit_size_filter, tuple)
        self.assertEquals(unit_size_filter[0], f"{search_terms[1][0]}__icontains")
        self.assertEquals(unit_size_filter[1], search_terms[1][1][0])

    def test_get_combined_filter_with_exclude(self):
        search_terms = [
            ('name', ('term1', 'term2')),
            ('unit_size', ('8oz', )),
            ('-name', ('exclude_term1', 'exclude_term2')),
        ]
        only_inclusive_search_terms = [st for st in search_terms if not st[0].startswith("-")]
        only_exclusive_search_terms = [st for st in search_terms if st[0].startswith("-")]
        combined_filter = inv_models.SourceItem.objects.get_combined_filter(search_terms)
        self.assertIsInstance(combined_filter, models.Q)
        self.validate_combined_filter(combined_filter, only_inclusive_search_terms)

        combined_exclude = inv_models.SourceItem.objects.get_combined_filter(search_terms, exclude_filter=True)
        print(f"\ncombined_exclude == {combined_exclude}")
        self.validate_combined_filter(combined_exclude, only_exclusive_search_terms)
