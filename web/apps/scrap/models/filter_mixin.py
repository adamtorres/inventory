from django.db import models

import uuid


class FilterMixin(object):
    autocomplete_fields = []
    filter_prefetch = []
    autocomplete_order = []
    filter_order = []
    autocomplete_initial_qs = None
    source_field = None
    department_field = None
    live_filter_keys_to_fields = {}

    def autocomplete_search(self, terms=None, sources=None, all_terms=True):
        """
        Provided a single or list of terms, search item names, common names, and other names for the terms.  Return a
        queryset of the found items.  Optionally filter on source(s) when provided with a single or list of UUIDs.

        Args:
            terms: single string or list of strings.
            sources: list of UUIDs as strings
            all_terms: True if all terms must appear in a searched field.  Order does not matter, just existence.

        Returns:
            queryset with the result.
        """
        # TODO: should .distinct() be part of this?  Default to whatever is in filter_order or 'id'?
        if not terms and not sources:
            return self.none()
        term_q = self.get_autocomplete_terms_filter(terms, all_terms=all_terms)
        source_q = self.get_source_filter(sources)
        if self.autocomplete_initial_qs:
            qs = getattr(self, self.autocomplete_initial_qs)()
        else:
            qs = self
        return self.order_autocomplete(qs.prefetch_related(*self.get_filter_prefetch()).filter(term_q, source_q))

    def order_autocomplete(self, qs):
        if self.autocomplete_order:
            qs = qs.order_by(*self.autocomplete_order)
        return qs

    def order_filter(self, qs):
        if self.filter_order:
            qs = qs.order_by(*self.filter_order)
        return qs

    def get_field_filter(self, field_name):
        # TODO: get_department_filter and get_source_filter are twins.  Find a way to make this generic.
        pass

    def get_department_filter(self, departments):
        if not departments or not self.department_field:
            return models.Q()
        if isinstance(departments, (str, uuid.UUID)):
            departments = [departments]
        department_q = models.Q()
        if departments != ['']:
            department_kwarg = f"{self.department_field}__id"
            for department in departments:
                department_q = department_q | models.Q(**{department_kwarg: department})
        return department_q

    def get_filter_prefetch(self):
        return self.filter_prefetch

    def get_source_filter(self, sources):
        if not sources or not self.source_field:
            return models.Q()
        if isinstance(sources, (str, uuid.UUID)):
            sources = [sources]
        source_q = models.Q()
        if sources != ['']:
            source_kwarg = f"{self.source_field}__id"
            for source in sources:
                source_q = source_q | models.Q(**{source_kwarg: source})
        return source_q

    def get_autocomplete_terms_filter(self, terms, all_terms=False):
        if not terms:
            return models.Q()
        if isinstance(terms, str):
            terms = terms.split()

        term_q = models.Q()
        for field in self.autocomplete_fields:
            field_q = models.Q()
            for term in terms:
                kwargs = {f"{field}__icontains": term}
                if all_terms:
                    field_q = field_q & models.Q(**kwargs)
                else:
                    field_q = field_q | models.Q(**kwargs)
            term_q = term_q | field_q
        return term_q

    def live_filter(self, sources=None, **kwargs):
        """
        Similar to the autocomplete except in that it searches more fields than just name and can keep the terms
        separated between same.

        Args:
            sources: filter by source(s)
            kwargs: any additional fields with associated values

        Returns:
            queryset
        """
        # if not terms and not sources:
        #     return self.none()
        combined_filter = models.Q()
        for key in self.live_filter_keys_to_fields.keys():
            if key not in kwargs:
                continue
            field_list = self.live_filter_keys_to_fields[key]
            if isinstance(field_list, str):
                field_list = [field_list]
            field_q = models.Q()
            for field in field_list:
                term_q = models.Q()
                for term in kwargs[key]:
                    if field == "id" or field.endswith("__id"):
                        term_q = term_q & models.Q(**{field: term})
                    else:
                        term_q = term_q & models.Q(**{f"{field}__icontains": term})
                field_q = field_q | term_q
            combined_filter = combined_filter & field_q
        combined_filter = combined_filter & self.get_source_filter(sources)
        combined_filter = combined_filter & self.get_department_filter(kwargs.get("departments", []))
        return self.order_filter(self.prefetch_related(*self.get_filter_prefetch()).filter(combined_filter))
