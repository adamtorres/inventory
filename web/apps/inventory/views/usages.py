from django import urls
from django.http import HttpResponseRedirect
from django.views import generic

from inventory import models as inv_models, forms as inv_forms


class UsageView(generic.TemplateView):
    """
    Goal: have a listing of usages showing total costs and if they've been made into a change and applied.
    """
    # template_name = "inventory/usage_list.html"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['on_page_title'] = "Usage Reports (template view)"
        return kwargs


class UsageReportCreateView(generic.CreateView):
    model = inv_models.Usage
    fields = ('who', 'action_date', )

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['on_page_title'] = "Create Usage Report"
        return kwargs


class UsageReportDetailView(generic.DetailView):
    model = inv_models.Usage

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['on_page_title'] = "Usage Report Detail"
        return kwargs

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.prefetch_related('items', 'items__item', 'items__item__common_item')
        return qs


class UsageReportListView(generic.ListView):
    model = inv_models.Usage

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs['on_page_title'] = "Usage Reports"
        return kwargs


class UsageReportEditView(generic.UpdateView):
    model = inv_models.Usage
    form_class = inv_forms.UsageReportForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['on_page_title'] = "Edit Usage Report"
        if self.request.method == 'GET':
            context["usageitemformset"] = inv_forms.UsageReportItemFormSet(instance=self.object)
        if self.request.method == 'POST':
            context["usageitemformset"] = inv_forms.UsageReportItemFormSet(self.request.POST, instance=self.object)
        return context

    def get_success_url(self):
        return urls.reverse('usage_report', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        context = self.get_context_data()
        if context["usageitemformset"].is_valid():
            context["usageitemformset"].save()
        else:
            # TODO: invalid usageitemformset?
            for k in self.request.POST.keys():
                if k.startswith("items"):
                    print(f"POST[{k}] = {self.request.POST[k]!r}")
            print(f'ERRORS: {context["usageitemformset"].errors}')
            pass
        form.save()
        return HttpResponseRedirect(self.get_success_url())
