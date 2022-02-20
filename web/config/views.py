from django.apps import apps
from django.views import generic

from incoming import models as inc_models, serializers as inc_serializers


class ExampleView(generic.TemplateView):
    template_name = "examples/hello.html"


class DropdownExampleView(generic.TemplateView):
    template_name = "examples/dropdown.html"


class AutocompleteTestOne(generic.TemplateView):
    template_name = "examples/autocomplete_test1.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        qs = inc_models.Source.objects.active_sources()
        context['sources'] = inc_serializers.SourceSerializer(qs, many=True).data
        return context
