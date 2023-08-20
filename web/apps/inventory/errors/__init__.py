import json


class UseTypeMismatchError(Exception):
    """ Use Type mismatch between requested and item. """
    requested_use_type = "[unknown]"
    item_use_type = "[unknown]"

    def __init__(self, requested_use_type, item_use_type):
        self.requested_use_type = requested_use_type
        self.item_use_type = item_use_type
        super().__init__(
            f"Use Type mismatch between requested({self.requested_use_type!r}) and item({self.item_use_type!r}).")


class InsufficientQuantityError(ValueError):
    remaining_quantity = 0
    requested_quantity = 0
    log_message = ""
    message_template = "Insufficient quantity({remaining_quantity}) to satisfy adjustment({requested_quantity})."
    message = ""

    def __init__(self, remaining_quantity, requested_quantity):
        self.remaining_quantity = remaining_quantity
        self.requested_quantity = requested_quantity
        self.message = self.message_template.format(
            remaining_quantity=remaining_quantity, requested_quantity=requested_quantity)
        self.log_message = json.dumps(
            {'remaining_quantity': remaining_quantity, 'requested_quantity': requested_quantity},
            sort_keys=True, default=str
        )
        super().__init__(self.message)
