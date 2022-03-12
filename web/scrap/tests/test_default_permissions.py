from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.views import generic

from .. import mixins as sc_mixins


class DefaultPermissionMixinTestCase(TestCase):
    test_models = {}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_models['single'] = cls.generate_model("fake_app_name", "model_one")
        cls.test_models['multiple'] = [
            cls.generate_model("fake_app_name", "model_one"),
            cls.generate_model("fake_app_name", "model_two"),
            ]

    @classmethod
    def generate_model(cls, app_name, model_name):
        return type("FakeModel", (object, ), {"_meta": f"{app_name}.{model_name}"})

    def test_detail_view(self):
        v = type("TestDetailView", (sc_mixins.DefaultPermissionMixin, generic.DetailView), {
            "model": self.test_models['single']})()
        self.assertFalse(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.model), {"fake_app_name.view_model_one"})
        self.assertEqual(v.get_permission_required(), ("fake_app_name.view_model_one", ))

    def test_detail_view_multiple_models(self):
        v = type("TestDetailView", (sc_mixins.DefaultPermissionMixin, generic.DetailView), {
            "models": self.test_models['multiple']})()
        self.assertFalse(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.models[0]), {"fake_app_name.view_model_one"})
        self.assertEqual(
            v.get_permission_required(), ("fake_app_name.view_model_one", "fake_app_name.view_model_two", ))

    def test_create_view(self):
        v = type("TestCreateView", (sc_mixins.DefaultPermissionMixin, generic.CreateView), {
            "model": self.test_models['single']})()
        self.assertTrue(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.model), {
            "fake_app_name.add_model_one", "fake_app_name.view_model_one"})
        self.assertEqual(v.get_permission_required(), (
            "fake_app_name.add_model_one", "fake_app_name.view_model_one", ))

    def test_create_view_multiple_models(self):
        v = type("TestCreateView", (sc_mixins.DefaultPermissionMixin, generic.CreateView), {
            "models": self.test_models['multiple']})()
        self.assertTrue(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(
            v.build_permission_for_model(v.models[0]), {"fake_app_name.add_model_one", "fake_app_name.view_model_one"})
        self.assertRaises(ImproperlyConfigured, v.get_permission_required)

    def test_delete_view(self):
        v = type("TestDeleteView", (sc_mixins.DefaultPermissionMixin, generic.DeleteView), {
            "model": self.test_models['single']})()
        self.assertFalse(v.is_create())
        self.assertTrue(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.model), {
            "fake_app_name.delete_model_one", "fake_app_name.view_model_one"})
        self.assertEqual(v.get_permission_required(), (
            "fake_app_name.delete_model_one", "fake_app_name.view_model_one", ))

    def test_delete_view_multiple_models(self):
        v = type("TestDeleteView", (sc_mixins.DefaultPermissionMixin, generic.DeleteView), {
            "models": self.test_models['multiple']})()
        self.assertFalse(v.is_create())
        self.assertTrue(v.is_delete())
        self.assertFalse(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(
            v.build_permission_for_model(v.models[0]), {
                "fake_app_name.delete_model_one", "fake_app_name.view_model_one"})
        self.assertRaises(ImproperlyConfigured, v.get_permission_required)

    def test_update_view(self):
        v = type("TestUpdateView", (sc_mixins.DefaultPermissionMixin, generic.UpdateView), {
            "model": self.test_models['single']})()
        self.assertFalse(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertTrue(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(v.build_permission_for_model(v.model), {
            "fake_app_name.change_model_one", "fake_app_name.view_model_one"})
        self.assertEqual(v.get_permission_required(), (
            "fake_app_name.change_model_one", "fake_app_name.view_model_one", ))

    def test_update_view_multiple_models(self):
        v = type("TestUpdateView", (sc_mixins.DefaultPermissionMixin, generic.UpdateView), {
            "models": self.test_models['multiple']})()
        self.assertFalse(v.is_create())
        self.assertFalse(v.is_delete())
        self.assertTrue(v.is_update())
        self.assertTrue(v.is_view())
        self.assertEqual(
            v.build_permission_for_model(v.models[0]), {
                "fake_app_name.change_model_one", "fake_app_name.view_model_one"})
        self.assertRaises(ImproperlyConfigured, v.get_permission_required)
