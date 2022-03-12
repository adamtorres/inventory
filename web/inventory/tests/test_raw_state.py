from django.test import TestCase
from django_extensions.management.debug_cursor import monkey_patch_cursordebugwrapper

from .. import models as inv_models


class RawStateTestCase(TestCase):
    fixtures = ['raw_state.json']
    _print_sql = False
    _mp = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if cls._print_sql:
            cls._mp = monkey_patch_cursordebugwrapper(
                print_sql=True, confprefix="SHELL_PLUS", print_sql_location=False)
            cls._mp.__enter__()

    @classmethod
    def tearDownClass(cls):
        if cls._print_sql:
            cls._mp.__exit__(None, None, None)
        super().tearDownClass()

    def test_next_state(self):
        # Check all states in STATES_ORDER to verify the order there matches the loaded fixture.
        for i in range(0, len(inv_models.RawState.STATES_ORDER)-1, 1):
            cur_state = inv_models.RawState.objects.get_by_name(inv_models.RawState.STATES_ORDER[i])
            next_state = inv_models.RawState.objects.get_by_name(inv_models.RawState.STATES_ORDER[i+1])
            with self.subTest(cur_state=cur_state, next_state=next_state):
                self.assertEqual(cur_state.next_state, next_state)

    def test_done_state(self):
        # Verify the done state's next_state is None.
        done_state = inv_models.RawState.objects.done_state()
        self.assertIsNone(done_state.next_state)

    def test_next_action(self):
        qs = inv_models.RawState.objects.prefetch_related('next_state')

        # Try the states which are not failures
        with_next_qs = qs.filter(failed=False).exclude(name=inv_models.RawState.DONE_STATE)
        for state in with_next_qs:
            next_action = state.next_action
            with self.subTest(next_action=next_action, state=state):
                self.assertIsNotNone(next_action)
                self.assertEqual(inv_models.RawState.action_to_state_name(next_action), state.next_state.name)

        # Try the states which are failures.
        failed_qs = qs.filter(failed=True)
        for state in failed_qs:
            next_action = state.next_action
            with self.subTest(next_action=next_action, state=state):
                self.assertIsNotNone(next_action)
                self.assertEqual(inv_models.RawState.action_to_state_name(next_action), state.next_state.name)
