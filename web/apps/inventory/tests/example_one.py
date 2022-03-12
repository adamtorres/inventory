from django.test import TestCase


class AnimalTestCase(TestCase):
    model = None

    def setUp(self) -> None:
        from inventory import models as inv_models
        self.model = inv_models.RawState
        states_in_reverse_order = ["last", "middle", "first"]
        prev_state = None
        for i, state_name in enumerate(states_in_reverse_order):
            cur_state = self.model.objects.create(name=state_name, value=len(states_in_reverse_order) - i)
            cur_state.next_state = prev_state or cur_state
            cur_state.save()
            prev_state = cur_state

    def test_bob(self):
        first_state = self.model.objects.get_by_name("first")
        middle_state = self.model.objects.get_by_name("middle")
        self.assertEqual(first_state.next_state, middle_state)
