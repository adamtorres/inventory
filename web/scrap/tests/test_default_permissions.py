from django.test import TestCase
from django.views import generic

from .. import mixins as sc_mixins


class DefaultPermissionMixinTestCase(TestCase):
    def generate_model(self, app_name, model_name):
        return type("FakeModel", (object, ), {"_meta": f"{app_name}.{model_name}"})

    def test_detail_view(self):
        v = type("TestDetailView", (sc_mixins.DefaultPermissionMixin, generic.DetailView), {"model": self.fake_model})()
        self.assertFalse(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.model), {"fake_app_name.view_fake_model_name"})
        self.assertEqual(v.get_permission_required(), ("fake_app_name.view_fake_model_name", ))

    def test_create_view(self):
        v = type("TestCreateView", (sc_mixins.DefaultPermissionMixin, generic.CreateView), {"model": self.fake_model})()
        self.assertTrue(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.model), {
            "fake_app_name.add_fake_model_name", "fake_app_name.view_fake_model_name"})
        self.assertEqual(v.get_permission_required(), (
            "fake_app_name.add_fake_model_name", "fake_app_name.view_fake_model_name", ))
