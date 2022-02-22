
def recalculate_incoming_item_group(sender, instance, *args, **kwargs):
    # used by post_save and post_delete.  The args don't quite line up but do so enough for what I need.
    instance.parent.recalculate_calculated_fields()
