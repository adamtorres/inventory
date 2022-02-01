from django.db import models

import uuid


class Usage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # TODO: who used, when
    who = models.CharField("Who used this stuff", max_length=1024, null=False, blank=False)

    def __str__(self):
        return f"{self.who} used items {self.id}"

    @staticmethod
    def autocomplete_search_fields():
        return "id__icontains", "who__icontains"
