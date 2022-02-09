# Specific item in an order/donation.
from .incoming_item import IncomingItem

# Groups items in an order/donation.
from .incoming_item_group import IncomingItemGroup

# Holds details about an order/donation that might be specific to the source.
from .incoming_item_group_detail import IncomingItemGroupDetail

# master list of items from providers.  This links to common items in inventory.
from .item import Item

# The provider: sysco, donator, broulims, etc.
from .source import Source

# Template for the details on orders/donations.
from .source_incoming_detail_template import SourceIncomingDetailTemplate


def most_recent_order_per_source():
    results = []
    for s in Source.objects.active_sources().order_by('name'):
        results.append({
            'object': s,
            'most_recent_order': s.most_recent_order(),
        })
    return results
