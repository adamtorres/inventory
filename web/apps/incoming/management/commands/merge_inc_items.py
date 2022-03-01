from django.core.management.base import BaseCommand

from incoming import models as inc_models


class Command(BaseCommand):
    help = """
    Merge two incoming.Items into one.

    Example Usage:
        python manage.py merge_inc_items --keep <uuid> --merge <uuid>
    """
    dry_run = False

    def add_arguments(self, parser):
        parser.add_argument(
            '-k',
            '--keep',
            action='store',
            dest='keep',
            help="The incoming.Item to keep",
            required=True
        )
        parser.add_argument(
            '-m',
            '--merge',
            action='store',
            dest='merge',
            help="The incoming.Item to merge into keep and then remove",
            required=True
        )
        parser.add_argument(
            '-r',
            '--remove',
            action='store_true',
            dest='remove',
            default=False,
            help="Once the merging is complete, remove the unused incoming.Item"
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            dest='dry_run',
            default=False,
            help="Show what would happen but make no changes."
        )

    def handle(self, *args, **options):
        keep_item_id = options.get('keep')
        merge_item_id = options.get('merge')
        remove_item = options.get('remove')
        self.dry_run = options.get('dry_run')
        if self.dry_run:
            print("!!! dry run !!!")
        print(
            f"Merging {merge_item_id} into {keep_item_id} and then {'removing' if remove_item else 'not removing'} the "
            "unused item.")
        merge_item = inc_models.Item.objects.get(id=merge_item_id)
        keep_item = inc_models.Item.objects.get(id=keep_item_id)
        self.move_merge_usages_to_keep(merge_item, keep_item)
        if remove_item:
            self.remove_merge_item(merge_item)

    def move_merge_usages_to_keep(self, merge_item, keep_item):
        print(f"Moving usages from {merge_item!r} to {keep_item!r}")
        print(f"\tPreparing {merge_item.incoming_items.count()} IncomingItems for update.")
        items_to_update = []
        for ii in merge_item.incoming_items.all():
            ii.item = keep_item
            items_to_update.append(ii)
        if self.dry_run:
            print(f"\tDry run: not updating {len(items_to_update)} IncomingItems.")
        else:
            print(f"\tUpdating {len(items_to_update)} IncomingItems.")
            inc_models.IncomingItem.objects.bulk_update(items_to_update, ["item"])

    def remove_merge_item(self, merge_item):
        print(f"Removing {merge_item!r}")
        if self.dry_run:
            print("\tDry run: not removing Item.")
        else:
            merge_item.delete()
            print("\tItem removed.")
