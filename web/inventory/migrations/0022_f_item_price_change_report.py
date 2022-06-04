from django.db import migrations


forward_sql = """
CREATE OR REPLACE FUNCTION f_item_price_change_report (
    p_startdate TIMESTAMP WITH TIME ZONE,
    p_enddate TIMESTAMP WITH TIME ZONE,
    p_selected_items VARCHAR[])
RETURNS TABLE (
    "id" BIGINT,
    "source_name" VARCHAR(1024),
    "category_name" VARCHAR(1024),
    "commonitem_name" VARCHAR(1024),
    "item_code" VARCHAR(1024),
    "ticked_item_code" TEXT,
    "name" VARCHAR(1024),
    "pack_quantity" NUMERIC(10, 4),
    "unit_size" VARCHAR(1024),
    "unit_quantity" INT,
    "first_order" DATE,
    "first_pack_price" NUMERIC(10, 4),
    "first_price_per_count" NUMERIC(10, 4),
    "last_order" DATE,
    "last_pack_price" NUMERIC(10, 4),
    "last_price_per_count" NUMERIC(10, 4),
    "pack_price_change" NUMERIC(10, 4),
    "orders" BIGINT,
    "total_spent" NUMERIC(10, 4)
)
AS $$
BEGIN
    RETURN QUERY
    WITH tall_data AS (
        SELECT
            "vw_incoming_items_with_prices"."id",
            "vw_incoming_items_with_prices"."source_name",
            "vw_incoming_items_with_prices"."department_name",
            -- A distinct order is a combination of source, order_number and _delivery_date as:
            -- * order_numbers *might* be duplicated between sources or over time from the same source
            -- * some sources don't have order_number so date is as detailed as it gets
            FORMAT('%s;%s;%s', "vw_incoming_items_with_prices"."source_name", "vw_incoming_items_with_prices"."order_number", "vw_incoming_items_with_prices"."delivery_date") AS "order_key",
            -- "vw_incoming_items_with_prices"."customer_number",
            "vw_incoming_items_with_prices"."order_number",
            -- "vw_incoming_items_with_prices"."po_text",
            "vw_incoming_items_with_prices"."delivery_date",
            -- "vw_incoming_items_with_prices"."total_price",
            -- "vw_incoming_items_with_prices"."total_packs",

            "vw_incoming_items_with_prices"."line_item_position",
            "vw_incoming_items_with_prices"."delivered_quantity",

            "vw_incoming_items_with_prices"."pack_quantity",
            -- "vw_incoming_items_with_prices"."rawitem_pack_quantity",
            "vw_incoming_items_with_prices"."pack_price",
            "vw_incoming_items_with_prices"."pack_tax",
            "vw_incoming_items_with_prices"."total_weight",

            "vw_incoming_items_with_prices"."category_name",
            "vw_incoming_items_with_prices"."item_code",
            -- "vw_incoming_items_with_prices"."extra_code",
            -- "vw_incoming_items_with_prices"."rawitem_item_code",
            -- "vw_incoming_items_with_prices"."rawitem_extra_code",
            "vw_incoming_items_with_prices"."name",
            -- "vw_incoming_items_with_prices"."rawitem_better_name",
            -- "vw_incoming_items_with_prices"."rawitem_name",
            "vw_incoming_items_with_prices"."commonitem_name",

            "vw_incoming_items_with_prices"."unit_size",
            -- "vw_incoming_items_with_prices"."rawitem_unit_size",
            "vw_incoming_items_with_prices"."unit_quantity",
            -- "vw_incoming_items_with_prices"."rawitem_unit_quantity",

            "vw_incoming_items_with_prices"."extended_price"
          FROM "vw_incoming_items_with_prices"
         WHERE (p_startdate IS NULL OR "vw_incoming_items_with_prices"."delivery_date" >= p_startdate)
           AND (p_enddate IS NULL OR "vw_incoming_items_with_prices"."delivery_date" <= p_enddate)
           AND "vw_incoming_items_with_prices"."commonitem_name" = ANY (p_selected_items)
    )
    , short_data AS (
        SELECT DISTINCT
            tall_data."source_name",
            tall_data."category_name",
            tall_data."commonitem_name",
            tall_data."item_code",
            FORMAT('''%s', tall_data."item_code") AS "ticked_item_code",
            tall_data."name",
            tall_data."pack_quantity",
            tall_data."unit_size",
            tall_data."unit_quantity",
            FIRST_VALUE(tall_data."delivery_date") OVER w AS "first_order",
            FIRST_VALUE(tall_data."pack_price") OVER w AS "first_pack_price",
            FIRST_VALUE(tall_data."total_weight") OVER w AS "first_total_weight",
            FIRST_VALUE(tall_data."extended_price") OVER w AS "first_extended_price",
            FIRST_VALUE(tall_data."delivered_quantity") OVER w AS "first_delivered_quantity",
            LAST_VALUE(tall_data."delivery_date") OVER w AS "last_order",
            LAST_VALUE(tall_data."pack_price") OVER w AS "last_pack_price",
            LAST_VALUE(tall_data."total_weight") OVER w AS "last_total_weight",
            LAST_VALUE(tall_data."extended_price") OVER w AS "last_extended_price",
            LAST_VALUE(tall_data."delivered_quantity") OVER w AS "last_delivered_quantity",
            COUNT(tall_data."order_key") OVER w AS "orders",
            SUM(tall_data."extended_price") OVER w AS "total_spent"
        FROM tall_data
        WINDOW w AS (
            PARTITION BY tall_data."source_name", tall_data."item_code", tall_data."name", tall_data."commonitem_name", tall_data."pack_quantity", tall_data."unit_size", tall_data."unit_quantity"
            ORDER BY tall_data."source_name", tall_data."item_code", tall_data."name", tall_data."commonitem_name", tall_data."pack_quantity", tall_data."unit_size", tall_data."unit_quantity", tall_data."delivery_date"
            RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        )
    )
    SELECT
        ROW_NUMBER() OVER () AS id,
        short_data."source_name",
        short_data."category_name",
        short_data."commonitem_name",
        short_data."item_code",
        short_data."ticked_item_code",
        short_data."name",
        short_data."pack_quantity",
        short_data."unit_size",
        short_data."unit_quantity",
        short_data."first_order",
        CASE
            WHEN short_data."first_total_weight" > 0
                -- If total_weight is populated, pack_price is already a $/weight value.
                THEN ROUND(short_data."first_extended_price" / short_data."first_delivered_quantity", 4)
            ELSE short_data."first_pack_price"
        END AS "first_pack_price",
        ROUND(
            CASE
                WHEN short_data."first_total_weight" > 0
                    -- If total_weight is populated, pack_price is already a $/weight value.
                    THEN short_data."first_pack_price"
                WHEN short_data."pack_quantity" > 0
                    THEN ROUND(short_data."first_pack_price" / short_data."pack_quantity", 4)
                ELSE short_data."first_pack_price"
            END / short_data."unit_quantity",
            4) AS "first_price_per_count",
        short_data."last_order",
        CASE
            WHEN short_data."last_total_weight" > 0
                -- If total_weight is populated, pack_price is already a $/weight value.
                THEN ROUND(short_data."last_extended_price" / short_data."last_delivered_quantity", 4)
            ELSE short_data."last_pack_price"
        END AS "last_pack_price",
        ROUND(
            CASE
                WHEN short_data."last_total_weight" > 0
                    -- If total_weight is populated, pack_price is already a $/weight value.
                    THEN short_data."last_pack_price"
                WHEN short_data."pack_quantity" > 0
                    THEN ROUND(short_data."last_pack_price" / short_data."pack_quantity", 4)
                ELSE short_data."last_pack_price"
            END / short_data."unit_quantity",
            4) AS "last_price_per_count",
        (
            CASE
                WHEN short_data."last_total_weight" > 0
                    -- If total_weight is populated, pack_price is already a $/weight value.
                    THEN ROUND(short_data."last_extended_price" / short_data."last_delivered_quantity", 4)
                ELSE short_data."last_pack_price"
            END
            - CASE
                WHEN short_data."first_total_weight" > 0
                    -- If total_weight is populated, pack_price is already a $/weight value.
                    THEN ROUND(short_data."first_extended_price" / short_data."first_delivered_quantity", 4)
                ELSE short_data."first_pack_price"
            END
        ) AS "pack_price_change",
        short_data."orders",
        short_data."total_spent"
    FROM short_data
    ORDER BY short_data."category_name", short_data."commonitem_name", short_data."name", short_data."unit_size", short_data."ticked_item_code"
    ;
END; $$ 

LANGUAGE 'plpgsql';
"""


reverse_sql = """
DROP FUNCTION IF EXISTS f_item_price_change_report(TIMESTAMP WITH TIME ZONE, TIMESTAMP WITH TIME ZONE, VARCHAR[]);
"""

example_usage = """
SELECT
    ((CURRENT_TIMESTAMP - FORMAT('12 months %s days', EXTRACT('days' FROM CURRENT_TIMESTAMP)-1)::INTERVAL)::DATE)::TIMESTAMP WITH TIME ZONE AS p_startdate,
    CURRENT_TIMESTAMP AS p_enddate,
    '{"butter", "ground beef", "corn", "cut green beans", "smoked boneless pit ham", "hamburger sesame buns", "sweetener packets", "semi sweet chocolate chips", "flour"}' AS p_selected_items
\gset

SELECT *
FROM f_item_price_change_report(:'p_startdate', :'p_enddate', '{"butter", "low fat milk cartons", "ground beef"}');
"""

# 'low fat milk cartons', 'low fat chocolate milk cartons', 'chocolate pudding', 'lemon pudding',
# 'nonstick spray', 'butter', 'margarine', 'margarine tubs', 'cool whip', 'sour cream', 'cream cheese', 'large eggs', 'eggs',
# 'flour',
# 'mixed vegetables', 'california vegetable blend', 'scandinavian vegetable blend', '5 way vegetable mix', 'fajita vegetables',
# 'diced mixed fruit', 'fruit cocktail', 'sliced peaches', 'diced pears', 'apple slices', 'crushed pineapple', 'pineapple chunks', 'pineapple slices', 'pineapple tidbits',
# 'country fried beef fritter', 'ground beef', 'beef top round',
# 'grape juice', 'apple juice', 'orange juice', 'cranberry cocktail juice',
# 'center cut pork chop boneless', 'center cut pork loin boneless', 'center cut pork loin boneless strap off', 'pork loin boneless rolled tied', 'center cut pork loin boneless strap on',
# 'chicken cordon bleu', 'frozen chicken breast', 'breaded chicken breast patty precooked'


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0021_vw_incoming_items'),
    ]

    operations = [
        migrations.RunSQL(forward_sql, reverse_sql=reverse_sql)
    ]
