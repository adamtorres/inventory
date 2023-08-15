import logging

from django import http, urls
from django.views import generic
from django.views.generic import edit as gen_edit

from scrap import utils as sc_utils

from recipe import models as rcp_models, forms as rcp_forms


logger = logging.getLogger(__name__)


class RecipeCloneView(generic.UpdateView):
    """
    From a recipe, click 'clone'.
    GET: show the values from the origin recipe.  Allow user to edit fields (only those directly on Recipe obj.)
    POST: run Recipe.clone on origin obj and shove that new instance through the form.save method.
    """
    # generic.UpdateView(SingleObjectTemplateResponseMixin, BaseUpdateView)
    #  BaseUpdateView(ModelFormMixin, ProcessFormView)
    #   ProcessFormView(View)
    #   ModelFormMixin(FormMixin, SingleObjectMixin)
    model = rcp_models.Recipe
    fields = [
        'name', 'source', 'description', 'reason_to_not_make', 'star_acceptance', 'star_effort', 'common_multipliers',
        'template'
    ]

    def form_valid(self, form):
        # Would normally save here but the goal is to clone the old and use the form to modify the new.
        obj = self.get_object()
        self.object = obj.clone(include_ingredients=True, include_steps=True, cleaned_data=form.cleaned_data)
        return http.HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method in ("POST", "PUT"):
            logger.debug(f"RecipeCloneView.get_form_kwargs:[data] = {kwargs['data']}")
        return kwargs

    def get_success_url(self):
        return urls.reverse('recipe:recipe_detail', args=(self.object.id,))


class RecipeCreateView(generic.CreateView):
    model = rcp_models.Recipe
    fields = [
        'name', 'source', 'description', 'reason_to_not_make', 'star_acceptance', 'star_effort', 'common_multipliers',
        'template',
    ]

    def get_success_url(self):
        return urls.reverse('recipe:recipe_detail', args=(self.object.id,))


class RecipeDeleteView(generic.DeleteView):
    queryset = rcp_models.Recipe.objects.all()

    def get_success_url(self):
        return urls.reverse('recipe:recipe_list')


class RecipeDetailView(generic.DetailView):
    queryset = rcp_models.Recipe.objects.all()


class RecipeListView(generic.ListView):
    queryset = rcp_models.Recipe.objects.recipes()


class RecipeTemplateListView(generic.ListView):
    template_name = "recipe/recipe_list.html"
    queryset = rcp_models.Recipe.objects.templates()


class RecipeUpdateView(generic.UpdateView):
    model = rcp_models.Recipe
    fields = [
        'name', 'source', 'description', 'reason_to_not_make', 'star_acceptance', 'star_effort', 'common_multipliers',
        'template'
    ]

    def get_success_url(self):
        return urls.reverse('recipe:recipe_detail', args=(self.object.id,))


class RecipeCommentUpdateView(generic.detail.SingleObjectMixin, generic.FormView):
    model = rcp_models.Recipe
    template_name = "recipe/recipe_comment_update.html"
    object = None

    def form_valid(self, form):
        form.save()
        # TODO: messages.add_message(blah)
        return http.HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO: Is this needed?  Or was this stubbed to add some logging?
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        # The base get_form does not pass the instance kwarg.
        return rcp_forms.RecipeCommentFormset(**self.get_form_kwargs(), instance=self.object)

    def get_success_url(self):
        return urls.reverse("recipe:recipe_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class RecipeIngredientUpdateView(generic.detail.SingleObjectMixin, generic.FormView):
    model = rcp_models.Recipe
    template_name = "recipe/recipe_ingredient_update.html"
    object = None

    def form_valid(self, form):
        for i, ingredient_form in enumerate(form.ordered_forms):
            ingredient_form.save(commit=False)
            ingredient_form.instance.ingredient_number = i + 1
            ingredient_form.save()  # Thought the form.save would handle this but ingredient_number wasn't changed.
        form.save()
        # TODO: messages.add_message(blah)
        return http.HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO: Is this needed?  Or was this stubbed to add some logging?
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        # The base get_form does not pass the instance kwarg.
        return rcp_forms.RecipeIngredientFormset(**self.get_form_kwargs(), instance=self.object)

    def get_success_url(self):
        return urls.reverse("recipe:recipe_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class RecipeStepUpdateView(generic.detail.SingleObjectMixin, generic.FormView):
    model = rcp_models.Recipe
    template_name = "recipe/recipe_step_update.html"
    object = None

    def form_valid(self, form):
        for i, step_form in enumerate(form.ordered_forms):
            step_form.save(commit=False)
            step_form.instance.step_number = i + 1
            step_form.save()  # Thought the form.save would handle this but step_number wasn't being changed.
        form.save()
        # TODO: messages.add_message(blah)
        return http.HttpResponseRedirect(self.get_success_url())

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # TODO: Is this needed?  Or was this stubbed to add some logging?
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        # The base get_form does not pass the instance kwarg.
        return rcp_forms.RecipeStepFormset(**self.get_form_kwargs(), instance=self.object)

    def get_success_url(self):
        return urls.reverse("recipe:recipe_detail", args=(self.object.id,))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
