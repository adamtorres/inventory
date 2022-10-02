from django import forms
from django.contrib.postgres import forms as pg_forms

# from inventory import models as inv_models


class SourceItemCreateLineItemForm(forms.Form):
    individual_weights = pg_forms.SimpleArrayField(
        forms.DecimalField(max_digits=8, decimal_places=4),  # inv_models.SourceItem.individual_weights
        required=False,
    )

    class Meta:
        pass
