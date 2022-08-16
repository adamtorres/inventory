from django.contrib.postgres import fields as pg_fields
from django.db import models

from scrap import models as sc_models
from scrap.models import fields as sc_fields


class CommonNameManager(sc_models.WideFilterManagerMixin, models.Manager):
    pass


class CommonName(sc_models.WideFilterModelMixin, sc_models.UUIDModel):
    wide_filter_fields = {
        'name': ['cryptic_name', 'verbose_name', 'common_names'],
    }

    # This might vary from order to order as RSM and Sysco have not been consistent.
    cryptic_name = sc_fields.CharField(blank=False, help_text="Source-specific name of item as it appears on invoices")

    # This doesn't change any of the words or order.  It might add words where completely missing.
    # Just changes things like "PORK LOIN BNLS CC STR/OFF" to "Pork loin boneless center cut strap off"
    verbose_name = sc_fields.CharField(blank=False, help_text="More human-readable name of the item")

    # Peanut Butter.  No brand, unit size, item code, source, location, etc.
    common_names = pg_fields.ArrayField(sc_fields.CharField(), null=False, default=list)

    objects = CommonNameManager()

    def __str__(self):
        return self.verbose_name or self.cryptic_name
