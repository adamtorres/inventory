import uuid

from django.contrib.contenttypes import fields as ct_fields
from django.contrib.contenttypes import models as ct_models
from django.db import models
from django.utils import timezone


class Change(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link this to a vendor order, donation, local store pickup, etc.  Actual instance of change, not the company.
    # This is the order or donation group object.  Not a specific item within.
    # This could also link to usage forms or inventory adjustments
    source_limit = (
        models.Q(app_label='incoming', model='incomingitemgroup')
        | models.Q(app_label='inventory', model='adjustment')
        | models.Q(app_label='inventory', model='usage')
    )
    source = ct_fields.GenericForeignKey('source_content_type', 'source_object_id')
    source_content_type = models.ForeignKey(
        ct_models.ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to=source_limit)
    source_object_id = models.UUIDField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, null=False, blank=False, editable=False)
    action_date = models.DateField(null=False, blank=False, default=timezone.now)
    applied_datetime = models.DateTimeField("The change been applied", null=True, blank=True)

    source_model_to_nice_name = {
        "incomingitemgroup": "Incoming Item Group",
        "adjustment": "Adjustment",
        "usage": "Usage",
    }

    class Meta:
        ordering = ["-action_date", "-created"]

# inventory change
#     - groups changes to items
#     - this isn't just incoming.  This includes usage forms.
#     link to specific order or donation in case we need to see an original

    def __str__(self):
        applied = "✓" if self.applied_datetime else ""

        if self.source:
            source_type = self.source_model_to_nice_name.get(self.source_content_type.model) or "?"
            return f"{applied}{source_type} - {self.source}"
        return f"{applied}Group of inventory changes {self.id}"

    def apply_changes(self):
        for i in self.items.exclude(applied_datetime__isnull=False):
            i.apply_change()
        if not self.items.filter(applied_datetime__isnull=True).exists():
            self.applied_datetime = timezone.now()
            self.save()

    def related_label(self):
        return f"Change ({self.id})"
