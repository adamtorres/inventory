from django.views import generic


class ExampleView(generic.TemplateView):
    template_name = "examples/hello.html"


class DropdownExampleView(generic.TemplateView):
    template_name = "examples/dropdown.html"
