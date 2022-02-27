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
        context = super().get_context_data(**kwargs)
        qs = inc_models.Source.objects.active_sources()
        context['sources'] = inc_serializers.SourceSerializer(qs, many=True).data
        return context


class TemplateFun(generic.TemplateView):
    template_name = "examples/ex_base.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hello'] = 'Hello world!'
        if kwargs.get('template_name'):
            self.template_name = f'examples/{kwargs.get("template_name")}.html'
        print(f"TemplateFun: {kwargs}")
        return context
