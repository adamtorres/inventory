import logging
import requests

from django import urls, shortcuts
from django.views import generic

from scrap import views as sc_views
from .. import forms as inv_forms, models as inv_models, serializers as inv_serializers
from .api_raw_incoming_order import RawIncomingOrderFilter


logger = logging.getLogger(__name__)


class RawIncomingOrderCreateView(sc_views.OnPageTitleMixin, generic.FormView, generic.TemplateView):
    template_name = "inventory/rawincomingorder_form.html"
    on_page_title = "Create Raw Incoming Order"
    form_class = inv_forms.RawIncomingOrderForm
    formset_class = inv_forms.RawIncomingItemFormset
    object = None

    def get_formset_class(self):
        """Return the form class to use."""
        return self.formset_class

    def get_formset(self, formset_class=None):
        """Return an instance of the formset to be used in this view."""
        if formset_class is None:
            formset_class = self.get_formset_class()
        # TODO: Does formset need its own get_formset_kwargs?
        return formset_class(**self.get_form_kwargs())

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        # This is copied from ModelFormMixin as we need to call the form's save but there isn't an actual model.
        self.object = form.save()
        return super().form_valid(form)

    # def get(self, request, *args, **kwargs):
    #     if 'form' in kwargs:
    #         logger.debug("RawIncomingOrderCreateView:Replacing form on GET.")
    #     kwargs['form'] = inv_forms.RawIncomingOrderForm()
    #     return super().get(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'formset' not in kwargs:
            context['formset'] = self.get_formset()
        logger.debug(f"RawIncomingOrderCreateView.get_context_data = {context}")
        return context

    def get_success_url(self):
        if hasattr(self, 'object') and getattr(getattr(self, 'object'), 'pk'):
            return urls.reverse("inventory:rawincomingorder_detail", kwargs={'pk': self.object.pk})
        return urls.reverse("inventory:rawincomingorder_list")

    def post(self, request, *args, **kwargs):
        logger.debug(f"RawIncomingOrderCreateView.POST: POST = {self.request.POST}")
        logger.debug(f"RawIncomingOrderCreateView.POST: args = {args}")
        logger.debug(f"RawIncomingOrderCreateView.POST: kwargs = {kwargs}")
        form = self.get_form()
        formset = self.get_formset()
        if form.is_valid() and formset.is_valid():
            obj = self.form_valid(form)
            what_does_this_return = formset.save()
            return obj
        else:
            return self.form_invalid(form)


class RawIncomingOrderDetailView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/rawincomingorder_detail.html"
    on_page_title = "Raw Incoming Order Detail"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logger.debug(f"RawIncomingOrderDetailView.get_context_data: {kwargs}")
        # api_get_data['format'] = 'json'
        relative_url = urls.reverse("inventory:api_rawincomingorder_detail", kwargs={'pk': kwargs['pk']})
        api_url = self.request.build_absolute_uri(relative_url)
        resp = requests.get(api_url)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        context['object'] = api_return_data
        return context


class RawIncomingOrderListView(sc_views.OnPageTitleMixin, generic.TemplateView):
    template_name = "inventory/rawincomingorder_list.html"
    on_page_title = "Raw Incoming Order List"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = []
        # copy any GET args for the api except 'format' as that will be forced to json
        api_get_data = {k: v for k, v in self.request.GET.items() if k in RawIncomingOrderFilter.Meta.fields}
        if "reset" in self.request.GET:
            self.request.session["order_filters"] = {}
        if not api_get_data:
            api_get_data = self.request.session.get("order_filters") or {}
        self.request.session["order_filters"] = api_get_data.copy()
        api_get_data['format'] = 'json'
        api_get_data['paging'] = 'off'
        api_url = self.request.build_absolute_uri(urls.reverse("inventory:api_rawincomingorder_list"))
        resp = requests.get(api_url, params=api_get_data)
        if resp.status_code != 200:
            return context
        api_return_data = resp.json()
        # TODO: Is it necessary to run the json through the serializer to get objects?  Using the dicts seems to work.
        # context['object_list'] = inv_serializers.RawIncomingOrderSerializer(api_return_data['results'], many=True).data
        if api_get_data['paging'] == 'off':
            # Unpaged results are not in an outer dict
            context['object_list'] = api_return_data
        else:
            context['object_list'] = api_return_data['results']
        return context

