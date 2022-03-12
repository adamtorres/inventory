import inspect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import ImproperlyConfigured


class DefaultPermissionMixin(PermissionRequiredMixin):
    """
    Uses inspect.getmro to look for the generic views to determine permissions to use.
    Adds those permissions to the manually set permission_required.
    """
    _mro = None
    permission_required = tuple()

    def _get_mro(self):
        if self._mro is None:
            mro = inspect.getmro(type(self))
            self._mro = {c.__name__ for c in mro}

    def is_create(self):
        self._get_mro()
        if {"BaseCreateView", "CreateView"}.intersection(self._mro):
            return True
        return False

    def is_delete(self):
        self._get_mro()
        if {"BaseDeleteView", "DeleteView"}.intersection(self._mro):
            return True
        return False

    def is_update(self):
        self._get_mro()
        if {"BaseUpdateView", "UpdateView"}.intersection(self._mro):
            return True
        return False

    def is_view(self):
        self._get_mro()
        if {"View", "BaseListView", "ListView", "BaseDetailView", "DetailView"}.intersection(self._mro):
            return True
        return False

    def build_permission_for_model(self, model):
        app_name, model_name = str(model._meta).split(".", 1)
        default_permissions = set()
        if self.is_create():
            default_permissions.add(f"{app_name}.add_{model_name}")
        if self.is_delete():
            default_permissions.add(f"{app_name}.delete_{model_name}")
        if self.is_update():
            default_permissions.add(f"{app_name}.change_{model_name}")
        if self.is_view():
            default_permissions.add(f"{app_name}.view_{model_name}")
        return default_permissions

    def get_permission_required(self):
        default_permissions = set()
        if hasattr(self, "model") and getattr(self, "model"):
            default_permissions.update(self.build_permission_for_model(self.model))
        if hasattr(self, "models") and getattr(self, "models"):
            if self.is_create() or self.is_update() or self.is_delete():
                raise ImproperlyConfigured(
                    f"{self.__class__.__name__} is based on Create, Update, or Delete views which require a single "
                    f"model.")
            for model in self.models:
                default_permissions.update(self.build_permission_for_model(model))
        manual_permissions = super().get_permission_required()
        # Sorting the tuple so tests can depend on the returned order.
        combined_permissions = tuple(sorted(default_permissions.union(manual_permissions)))
        return combined_permissions
