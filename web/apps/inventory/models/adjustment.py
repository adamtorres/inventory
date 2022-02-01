from django.db import models

import uuid


class Adjustment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: what kind of adj (audit, damaged, other group-level thing), when
    type = models.CharField("Adjustment type", max_length=1024, null=False, blank=False)

    def __str__(self):
        return f"a set of {self.type} items {self.id}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "type__icontains"