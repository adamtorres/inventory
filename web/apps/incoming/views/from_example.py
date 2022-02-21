from django.shortcuts import render
from django.views.generic import (TemplateView, ListView, CreateView, DetailView, FormView)
from django.contrib import messages
from django.urls import reverse
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponseRedirect

from incoming import models as inc_models, forms as inc_forms
# inc_forms.IncomingItemFormSet


class ExampleIncomingItemGroupCreateView(CreateView):
    model = inc_models.IncomingItemGroup
    template_name = 'incoming/example_create.html'
    fields = ['source', 'descriptor', 'comment', 'action_date']

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            'The incoming item group has been added'
        )

        return super().form_valid(form)


class ExampleIncomingItemGroupEditView(SingleObjectMixin, FormView):
    model = inc_models.IncomingItemGroup
    template_name = 'incoming/example_edit.html'
    form_class = inc_forms.IncomingGroupForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            context["itemformset"] = inc_forms.IncomingItemFormSet(instance=self.object)
        if self.request.method == 'POST':
            context["itemformset"] = inc_forms.IncomingItemFormSet(self.request.POST, instance=self.object)
        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        return inc_forms.IncomingGroupForm(**self.get_form_kwargs(), instance=self.object)

    def form_valid(self, form):
        context = self.get_context_data()
        if context["itemformset"].is_valid():
            context["itemformset"].save()
        else:
            # TODO: invalid itemformset?
            pass
        form.save()

        messages.add_message(
            self.request,
            messages.SUCCESS,
            'Changes were saved.'
        )

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('incoming_group', kwargs={'pk': self.object.pk})
