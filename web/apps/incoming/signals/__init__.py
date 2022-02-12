
def recalculate_incoming_item_group(sender, instance, created, **kwargs):
    instance.parent.recalculate_calculated_fields()
