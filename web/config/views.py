from django.views import generic


class PlaceholderView(generic.TemplateView):
    template_name = "placeholder.html"
