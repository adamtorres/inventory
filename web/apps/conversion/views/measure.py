from django import urls
from django.views import generic

from conversion import models as con_models, forms as con_forms


class MeasureCreateView(generic.CreateView):
    model = con_models.Measure
    form_class = con_forms.MeasureForm

    def get_success_url(self):
        return urls.reverse('conversion:measure_detail', args=(self.object.id,))


class MeasureDetailView(generic.DetailView):
    model = con_models.Measure


class MeasureListView(generic.ListView):
    model = con_models.Measure
