class QuerysetExtrasMixin:
    order_fields = []
    prefetch_fields = []

    def order_qs(self, qs):
        if self.order_fields:
            return qs.order_by().order_by(*self.order_fields)
        return qs

    def prefetch_qs(self, qs):
        if self.prefetch_fields:
            return qs.prefetch_related(*self.prefetch_fields)
        return qs
