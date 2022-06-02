from django.db import migrations


forward_sql = """
-- Goal: Provide a common set of joins so other queries can make use of the Django models more easily

CREATE OR REPLACE VIEW vw_incoming_items AS
-- This returns all items including donated and backordered items.
SELECT
    "inventory_rawincomingitem".*,
    "inventory_category"."name" AS "category_name",
    "inventory_department"."name" AS "department_name",
    "inventory_source"."name" AS "source_name",
    "inventory_rawitem"."name" AS "rawitem_name",
    "inventory_commonitemname"."name" AS "commonitem_name",
    "inventory_rawitem"."unit_size" AS "rawitem_unit_size",
    "inventory_rawitem"."pack_quantity" AS "rawitem_pack_quantity",
    "inventory_rawitem"."unit_quantity" AS "rawitem_unit_quantity",
    "inventory_rawitem"."better_name" AS "rawitem_better_name",
    "inventory_rawitem"."item_code" AS "rawitem_item_code",
    "inventory_rawitem"."extra_code" AS "rawitem_extra_code",
    "inventory_rawitem"."item_comment" AS "rawitem_item_comment"
FROM "inventory_rawincomingitem"
INNER JOIN "inventory_rawitem"
    ON ("inventory_rawincomingitem"."rawitem_obj_id" = "inventory_rawitem"."id")
LEFT OUTER JOIN "inventory_category"
    ON ("inventory_rawincomingitem"."category_obj_id" = "inventory_category"."id")
LEFT OUTER JOIN "inventory_department"
    ON ("inventory_rawincomingitem"."department_obj_id" = "inventory_department"."id")
LEFT OUTER JOIN "inventory_source"
    ON ("inventory_rawincomingitem"."source_obj_id" = "inventory_source"."id")
INNER JOIN "inventory_commonitemnamegroup"
    ON ("inventory_rawitem"."common_item_name_group_id" = "inventory_commonitemnamegroup"."id")
INNER JOIN "inventory_commonitemname"
    ON ("inventory_commonitemnamegroup"."name_id" = "inventory_commonitemname"."id")
;

CREATE OR REPLACE VIEW vw_incoming_items_with_prices AS
SELECT *
FROM vw_incoming_items
WHERE NOT (("po_text" = 'donation' OR "delivered_quantity" = 0))
;
"""

reverse_sql = """
DROP VIEW IF EXISTS vw_incoming_items_with_prices;
DROP VIEW IF EXISTS vw_incoming_items;
"""


class Migration(migrations.Migration):
    dependencies = [
        ('inventory', '0020_reportsetting_alter_rawincomingitem_state'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql)
    ]
