# by_pack would mean each use is (pack_quantity) of (unit_size)
# by_unit would mean each use is (unit_size)
# by_count would mean each use is a subdivision of unit_size if available.
#   Some products have a 'lb' unit_size but would not make sense to break down to that level.
#   Others, like #10 cans, are a single unit and should not be subdivided.

# Example:
# Order 385651775, "labella pasta noodle egg xwide"
#   delivered_quantity=3, pack_quantity=2, unit_size=5lb, unit_quantity=5
# by_pack would mean each use is 2(pack_quantity) 5lb(unit_size) units for a total of 10lb of egg noodle.
# by_unit would mean each use is 1 5lb unit
# by_count would mean each use is 1lb - would not make sense for this product.

# Example:
# Order 485212206, "whlfcls egg shell large white"
#   delivered_quantity=1, pack_quantity=1, unit_size=30dz, unit_quantity=360
# by_pack would mean each use is 1(pack_quantity) unit of 30dz(unit_size) eggs
# by_unit would mean each use is 1 30dz(unit_size) of eggs
# by_count would mean 1 egg makes sense for this product.

# Example:
# Order 485292245, "sys cls bean green cut 4sv bl fcy"
#   delivered_quantity=3, pack_quantity=6, unit_size=#10, unit_quantity=1
# by_pack would mean each use is 6(pack_quantity) unit of #10(unit_size) cans
# by_unit would mean each use is 1 #10(unit_size) of cans
# by_count would not make sense for this product as a single #10 can cannot be subdivided.

BY_PACK = 'BP'
BY_UNIT = 'BU'
BY_COUNT = 'BC'
USE_TYPE_CHOICES = [
    (BY_PACK, 'By Pack'),
    (BY_UNIT, 'By Unit'),
    (BY_COUNT, 'By Count'),
]

USE_TYPE_TRANSLATE = {k: v for k, v in USE_TYPE_CHOICES}


def use_type_to_str(use_type):
    return USE_TYPE_TRANSLATE.get(use_type, None)


def use_type_to_single_word(use_type):
    return USE_TYPE_TRANSLATE.get(use_type, '')[3:].lower()
