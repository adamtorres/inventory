from django.db import models

import uuid


class FilterMixin(object):
    fields_to_filter_with_terms = []
    filter_prefetch = []
    filter_order = []
    filter_initial_qs = None
    source_field = None

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
        term_q = self.get_terms_filter(terms, all_terms=all_terms)
        source_q = self.get_source_filter(sources)
        if self.filter_initial_qs:
            qs = getattr(self, self.filter_initial_qs)()
        else:
            qs = self
        return self.order_filter(qs.prefetch_related(*self.get_filter_prefetch()).filter(term_q, source_q))

    def order_filter(self, qs):
        if self.filter_order:
            qs = qs.order_by(*self.filter_order)
        return qs

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

    def get_terms_filter(self, terms, all_terms=False):
        if not terms:
            return models.Q()
        if isinstance(terms, str):
            terms = terms.split()

        term_q = models.Q()
        for field in self.fields_to_filter_with_terms:
            field_q = models.Q()
            for term in terms:
                kwargs = {f"{field}__icontains": term}
                if all_terms:
                    field_q = field_q & models.Q(**kwargs)
                else:
                    field_q = field_q | models.Q(**kwargs)
            term_q = term_q | field_q
        return term_q

    def live_filter(self, terms=None, sources=None):
        """
        Similar to the autocomplete except in that it searches more fields than just name and can keep the terms
        separated between same.

        Args:
            terms:
            sources:

        Returns:

        """
        # TODO: terminology conflict with autocomplete attributes.
        pass
