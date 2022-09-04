class UseTypeMismatchError(Exception):
    """ Use Type mismatch between requested and item. """
    requested_use_type = "[unknown]"
    item_use_type = "[unknown]"

    def __init__(self, requested_use_type, item_use_type):
        self.requested_use_type = requested_use_type
        self.item_use_type = item_use_type
        super().__init__(
            f"Use Type mismatch between requested({self.requested_use_type!r}) and item({self.item_use_type!r}).")
