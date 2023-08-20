from django.db import models

from ..common import use_type
from scrap import models as sc_models
from scrap.models import fields as sc_fields


class UseTypeOverrideManager(models.Manager):
    pass


class UseTypeOverride(sc_models.UUIDModel):
    source = models.ForeignKey("inventory.Source", null=True, blank=True, on_delete=models.CASCADE)
    cryptic_name = sc_fields.CharField(
        null=True, blank=True, help_text="Source-specific name of item as it appears on invoices")
    verbose_name = sc_fields.CharField(null=True, blank=True, help_text="More human-readable name of the item")
    item_code = sc_fields.CharField(
        null=True, blank=True, help_text="String of text that should uniquely identify the item")
    extra_code = sc_fields.CharField(null=True, blank=True, help_text="A second code or whatever.")

    use_type = models.CharField(max_length=2, choices=use_type.USE_TYPE_CHOICES, default=use_type.BY_PACK)

    class Meta:
        pass

    def __str__(self):
        criteria = []
        if self.source is not None:
            criteria.append("(source)")
        for f in ['cryptic_name', 'verbose_name', 'item_code', 'extra_code']:
            v = getattr(self, f)
            if v:
                criteria.append(f"{f}={v!r}")
        return (":".join(criteria) or "(no criteria)") + f" = {self.use_type}"

    def source_item_filter(self):
        si_filter = models.Q()
        for f in ['source', 'cryptic_name', 'verbose_name', 'item_code', 'extra_code']:
            # This avoids hitting the source table for the record as it isn't needed.
            _f = f"{f}_id" if f in ['source'] else f
            v = getattr(self, _f)
            if v:
                modifier = ''
                # Some fields are to be used as wildcards.  Item_code should not.
                modifier = '__icontains' if _f in ['cryptic_name', 'verbose_name'] else modifier
                si_filter &= models.Q(**{f"{_f}{modifier}": v})
        return si_filter
