from django.core import exceptions
from django.db import models

from scrap import utils as sc_utils


class WideFilterManagerMixin:
    def wide_filter(self, search_terms):
        """
        Casts a wide net to find records and hence a 'wide_filter'.
        search_terms is a list of tuples where each for each tuple [0] is the field and [1] is a str/iterable of terms.
        Individual words should be separate terms.
        search_terms = [
            ('name', ('ground', 'beef')),
            ('category', 'meats'),
        ]
        Will search all relations listed in model.filter_fields['name'] for 'ground' and 'beef'.
        A name which has just 'beef' will not match.
        """
        combined_filter = models.Q()
        for field, terms in search_terms:
            if field == 'all':
                # ignore all other fields specified in search_terms.  Using only the terms on 'all', iterate over all
                # available wide filter fields on the model.
                # Important difference! This returns an ORed filter meaning the search terms do not have to be in all
                # the various fields but all the terms still have to be in an individual field.
                combined_filter = models.Q()
                for all_field in self.model.get_available_wide_filters():
                    if all_field == 'all':
                        continue
                    combined_filter = combined_filter | self.model.get_wide_filter(terms, wide_filter_name=all_field)
                break
            combined_filter = combined_filter & self.model.get_wide_filter(terms, wide_filter_name=field)
        qs = self.filter(combined_filter).order_by().distinct('id')
        # Use the above qs as the filter for a clean queryset.  This allows users of the wide_filter to do whatever
        # they want and not have to tiptoe around the distinct clause.
        # Ex:
        # RawItem.objects.wide_filter([('name', ('burger', 'bun'))]).order_by('name')
        # instead of:
        # RawItem.objects.filter(id__in=RawItem.objects.wide_filter([('name', ('burger', 'bun'))])).order_by('name')
        return self.filter(id__in=qs)


class WideFilterModelMixin:
    # wide_filter_fields = {
    #     'name': [
    #         'name', 'better_name', 'common_item_name_group__uncommon_item_names',
    #         'common_item_name_group__names__name'],
    #     'category': 'category__name',
    # }
    # wide_filter_fields_any = ["list of above keys which should be" "or'ed", "instead of", "and'ed"]

    @classmethod
    def get_available_wide_filters(cls):
        if not hasattr(cls, 'wide_filter_fields') or not isinstance(getattr(cls, 'wide_filter_fields'), dict):
            raise exceptions.ImproperlyConfigured("wide_filter_fields must be declared on the model.")
        return list(cls.wide_filter_fields.keys())

    @classmethod
    def get_wide_filter(cls, search_terms, wide_filter_name='name'):
        wide_filter_fields = cls.get_wide_filter_fields(wide_filter_name)
        q = models.Q()
        if isinstance(wide_filter_fields, str):
            wide_filter_fields = [wide_filter_fields]
        for field in wide_filter_fields:
            if isinstance(search_terms, str):
                # TODO: should this split the str?
                search_terms = [search_terms]
            term_q = models.Q()
            for search_term in search_terms:
                filter_func = "__icontains" if isinstance(search_term, str) else ""
                if field == 'id' or field.endswith('_id'):
                    # UUID doesn't like icontains
                    filter_func = ""
                    if not sc_utils.is_valid_uuid(search_term):
                        # Not a valid uuid so shouldn't be used to filter on uuid fields.
                        continue
                if wide_filter_name in cls.wide_filter_fields_any:
                    term_q = term_q | models.Q(**{f"{field}{filter_func}": search_term})
                else:
                    term_q = term_q & models.Q(**{f"{field}{filter_func}": search_term})
            q = q | term_q
        return q

    @classmethod
    def get_wide_filter_fields(cls, wide_filter_name):
        if not hasattr(cls, 'wide_filter_fields') or not isinstance(getattr(cls, 'wide_filter_fields'), dict):
            raise exceptions.ImproperlyConfigured("wide_filter_fields must be declared on the model.")
        return cls.wide_filter_fields[wide_filter_name]
