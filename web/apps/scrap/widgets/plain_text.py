from django import forms


class PlainText(forms.Widget):
    template_name = 'scrap/widgets/plain_text.html'

    def __init__(self, attrs=None):
        default_attrs = {}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
