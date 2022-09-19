__all__ = [
    'ITEM_CATEGORIES', 'ITEM_CATEGORY_COOKIE', 'ITEM_CATEGORY_CAKE', 'ITEM_CATEGORY_BREAD', 'ITEM_CATEGORY_OTHER',
    'get_suggested_price'
]

ITEM_CATEGORY_COOKIE = "cookie"
ITEM_CATEGORY_CAKE = "cake"
ITEM_CATEGORY_BREAD = "bread"
ITEM_CATEGORY_OTHER = "other"
ITEM_CATEGORIES = [
    (ITEM_CATEGORY_BREAD, "Bread"),
    (ITEM_CATEGORY_CAKE, "Cake"),
    (ITEM_CATEGORY_COOKIE, "Cookie"),
    (ITEM_CATEGORY_OTHER, "Other"),
]

# TODO: Make this somehow a setting changeable via the UI.
suggested_prices = {
    ITEM_CATEGORY_COOKIE: {
        3: 1.75,
        6: 3,
        12: 6,
    },
    ITEM_CATEGORY_BREAD: {
        1: 4,  # loaf
        8: 4,  # hamburger bun
        12: 4,  # rolls / breadsticks
    },
}


def get_suggested_price(category, quantity):
    category_prices = suggested_prices.get(category) or {}
    return category_prices.get(quantity)
