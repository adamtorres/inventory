from django.db import models

from scrap import fields as sc_fields, models as sc_models


class RawStateManager(models.Manager):
    def get_by_natural_key(self, value):
        return self.get(value=value)

    def get_by_action(self, action):
        return self.get(name=self.model.action_to_state_name(action))

    def get_by_name(self, name):
        return self.get(name=name)

    def failed_states(self):
        return self.filter(name__in=self.model.FAILED_STATES)

    def done_state(self):
        return self.get(name=self.model.DONE_STATE)


class RawState(sc_models.UUIDModel):
    """
    ./manage.py dumpdata --format json --indent 2 --output apps/inventory/fixtures/raw_state.json inventory.RawState
    """
    name = sc_fields.CharField(blank=False, help_text="short name of the status")
    description = sc_fields.CharField(help_text="Short description of the status")
    value = models.IntegerField(null=False, blank=False, help_text="incrementing value to help sort progress")
    next_state = models.ForeignKey(
        "RawState", on_delete=models.SET_NULL, related_name="prev_state", null=True, blank=True)
    next_error_state = models.ForeignKey(
        "RawState", on_delete=models.SET_NULL, related_name="reset_state", null=True, blank=True)

    objects = RawStateManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(name="unique_raw_state_value", fields=('value', ))
        ]
        ordering = ('value', )

    STATES_ORDER = [
        "untouched", "cleaned", "calculated", "new_values_created", "done"]
    FAILED_STATES = ["failed_clean", "failed_calculation", "failed_creation", "failed_import"]
    DONE_STATE = "done"

    STATES_TO_ACTIONS = {
        # state to action
        "cleaned": "clean",
        "calculated": "calculate",
        "new_values_created": "create",
        "done": "import",
    }
    ACTIONS_TO_STATES = {
        # action to state
        "clean": "cleaned",
        "calculate": "calculated",
        "create": "new_values_created",
        "import": "done",
    }

    def __str__(self):
        return f"({self.value}) {self.name}"

    def __ge__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot compare {type(other)} and {type(self)}")
        return self.value >= other.value

    def __gt__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot compare {type(other)} and {type(self)}")
        return self.value > other.value

    def __le__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot compare {type(other)} and {type(self)}")
        return self.value <= other.value

    def __lt__(self, other):
        if not isinstance(other, type(self)):
            raise TypeError(f"Cannot compare {type(other)} and {type(self)}")
        return self.value < other.value

    @property
    def next_action(self, retry_failed=False):
        if not retry_failed and self.next_state in self.FAILED_STATES:
            return None
        if self.next_state is None:
            return None
        next_action = self.STATES_TO_ACTIONS.get(self.next_state.name)
        if next_action is None:
            # TODO: should this raise an error?
            return None
        return next_action

    @classmethod
    def action_to_state_name(cls, action):
        state_name = cls.ACTIONS_TO_STATES.get(action)
        if state_name is None:
            raise ValueError(f"Unrecognized action {action!r}")
        return state_name


def dump_states():
    for rs in RawState.objects.all().order_by('value'):
        bits = [
            str(rs).ljust(29),
            "next_error=" + (str(rs.next_error_state) or '').ljust(29),
            "next=" + (str(rs.next_state) or '').ljust(29),
            "next_action=" + str(rs.next_action),
        ]
        print(" / ".join(bits))
