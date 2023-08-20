from django import forms

from inventory import models as inv_models


class SourceItemAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['individual_weights'].required = False

    class Meta:
        model = inv_models.SourceItem
        fields = '__all__'
