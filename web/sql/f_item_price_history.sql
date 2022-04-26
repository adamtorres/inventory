-- gset ending a query will store the results into variables using the names of the fields.
SELECT
    ((CURRENT_TIMESTAMP - FORMAT('12 months %s days', EXTRACT('days' FROM CURRENT_TIMESTAMP)-1)::INTERVAL)::DATE)::TIMESTAMP WITH TIME ZONE AS p_startdate,
    CURRENT_TIMESTAMP AS p_enddate,
    '{"butter", "ground beef", "corn", "cut green beans", "smoked boneless pit ham", "hamburger sesame buns", "sweetener packets", "semi sweet chocolate chips", "flour"}' AS p_selected_items
\gset

WITH date_range AS (
    SELECT "month_bucket"::DATE
    FROM generate_series(:'p_startdate', :'p_enddate', '1 month'::INTERVAL) "month_bucket"
),
selected_items AS (
    SELECT DISTINCT
        "inventory_category"."name" AS "category",
        "inventory_rawitem"."unit_size",
        "inventory_commonitemname"."name",
        CASE
            WHEN "inventory_rawitem"."unit_size" <> ''
                THEN FORMAT('%s, %s', "inventory_commonitemname"."name", "inventory_rawitem"."unit_size")
            ELSE "inventory_commonitemname"."name"
        END AS "name_and_unit_size"
    FROM "inventory_rawitem"
    INNER JOIN "inventory_category"
        ON ("inventory_rawitem"."category_id" = "inventory_category"."id")
    INNER JOIN "inventory_commonitemnamegroup"
        ON ("inventory_rawitem"."common_item_name_group_id" = "inventory_commonitemnamegroup"."id")
    INNER JOIN "inventory_commonitemname"
        ON ("inventory_commonitemnamegroup"."name_id" = "inventory_commonitemname"."id")
    WHERE ("inventory_commonitemname"."name" = ANY (:'p_selected_items'))
),
by_month_empty_set AS (
    SELECT *,
        0 AS "orders",
        0 AS "total_count_quantity",
        0 AS "total_unit_quantity",
        0 AS "total_extended_price",
        0 AS "first_count_price",
        0 AS "first_unit_price"
    FROM selected_items, date_range
),
line_items AS (
    SELECT
        ("inventory_rawincomingitem"."delivery_date" - FORMAT('%s days', EXTRACT('days' FROM "inventory_rawincomingitem"."delivery_date")-1)::INTERVAL)::DATE AS "month_bucket",
        -- "inventory_rawincomingitem"."delivery_date",
        "inventory_category"."name" AS "category",
        CASE
            WHEN "inventory_rawitem"."unit_size" <> ''
                THEN FORMAT('%s, %s', "inventory_commonitemname"."name", "inventory_rawitem"."unit_size")
            ELSE "inventory_commonitemname"."name"
        END AS "name_and_unit_size",
        FORMAT(
            '%s;%s;%s',
            "inventory_rawincomingitem"."source",
            "inventory_rawincomingitem"."order_number",
            "inventory_rawincomingitem"."delivery_date"
        ) AS "order_key",
        "inventory_rawincomingitem"."delivered_quantity" * "inventory_rawitem"."pack_quantity" * "inventory_rawitem"."unit_quantity" AS "calculated_count_quantity",
        "inventory_rawincomingitem"."delivered_quantity" * "inventory_rawitem"."pack_quantity" AS "calculated_unit_quantity",
        "inventory_rawincomingitem"."extended_price",
        FIRST_VALUE(
            "inventory_rawincomingitem"."extended_price" / (
                "inventory_rawincomingitem"."delivered_quantity" * "inventory_rawitem"."pack_quantity" * "inventory_rawitem"."unit_quantity"
            )
        ) OVER w AS "first_count_price",
        FIRST_VALUE(
            "inventory_rawincomingitem"."extended_price" / (
                "inventory_rawincomingitem"."delivered_quantity" * "inventory_rawitem"."pack_quantity"
            )
        ) OVER w AS "first_unit_price"

    FROM "inventory_rawincomingitem"
    INNER JOIN "inventory_rawitem"
        ON ("inventory_rawincomingitem"."rawitem_obj_id" = "inventory_rawitem"."id")
    INNER JOIN "inventory_category"
        ON ("inventory_rawitem"."category_id" = "inventory_category"."id")
    INNER JOIN "inventory_commonitemnamegroup"
        ON ("inventory_rawitem"."common_item_name_group_id" = "inventory_commonitemnamegroup"."id")
    INNER JOIN "inventory_commonitemname"
        ON ("inventory_commonitemnamegroup"."name_id" = "inventory_commonitemname"."id")
    WHERE
        "inventory_rawincomingitem"."extended_price" > 0
        AND "inventory_rawincomingitem"."delivered_quantity" > 0
        AND (:'p_startdate' IS NULL OR "inventory_rawincomingitem"."delivery_date" >= :'p_startdate')
        AND (:'p_enddate' IS NULL OR "inventory_rawincomingitem"."delivery_date" <= :'p_enddate')
        AND ("inventory_commonitemname"."name" = ANY (:'p_selected_items'))
    WINDOW w AS (
        PARTITION BY "inventory_category"."name", "inventory_commonitemname"."name", "inventory_rawitem"."unit_size", ("inventory_rawincomingitem"."delivery_date" - FORMAT('%s days', EXTRACT('days' FROM "inventory_rawincomingitem"."delivery_date")-1)::INTERVAL)::DATE
        ORDER BY "inventory_category"."name", "inventory_commonitemname"."name", "inventory_rawitem"."unit_size", ("inventory_rawincomingitem"."delivery_date" - FORMAT('%s days', EXTRACT('days' FROM "inventory_rawincomingitem"."delivery_date")-1)::INTERVAL)::DATE, "inventory_rawincomingitem"."delivery_date"
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    )
),
by_month_and_item_with_gaps AS (
    SELECT
        "category", "month_bucket", "name_and_unit_size", "first_count_price", "first_unit_price",
        COUNT(DISTINCT "order_key") AS "orders",
        SUM("calculated_count_quantity") AS "total_count_quantity",
        SUM("calculated_unit_quantity") AS "total_unit_quantity",
        SUM("extended_price") AS "total_extended_price"
    FROM line_items
    GROUP BY "category", "month_bucket", "name_and_unit_size", "first_count_price", "first_unit_price"
),
by_month_and_item AS (
    SELECT
        a."category",
        a."name_and_unit_size",
        a."month_bucket",
        COALESCE(b."orders", a."orders") AS "orders",
        COALESCE(b."total_count_quantity", a."total_count_quantity") AS "total_count_quantity",
        COALESCE(b."total_unit_quantity", a."total_unit_quantity") AS "total_unit_quantity",
        COALESCE(b."total_extended_price", a."total_extended_price") AS "total_extended_price",
        COALESCE(b."first_count_price", a."first_count_price") AS "first_count_price",
        COALESCE(b."first_unit_price", a."first_unit_price") AS "first_unit_price"
    FROM by_month_empty_set a
    LEFT JOIN by_month_and_item_with_gaps b
        ON (a."category" = b."category")
        AND (a."name_and_unit_size" = b."name_and_unit_size")
        AND (a."month_bucket" = b."month_bucket")
),
flatten AS (
    SELECT
        by_month_and_item."category", by_month_and_item."name_and_unit_size",
        ARRAY_AGG(by_month_and_item."month_bucket") AS "months",
        ARRAY_AGG(by_month_and_item."orders") AS "orders",
        ARRAY_AGG(by_month_and_item."total_count_quantity") AS "total_count_quantity",
        ARRAY_AGG(by_month_and_item."total_unit_quantity") AS "total_unit_quantity",
        ARRAY_AGG(by_month_and_item."total_extended_price") AS "total_extended_price",
        ARRAY_AGG(by_month_and_item."first_count_price") AS "first_count_price",
        ARRAY_AGG(by_month_and_item."first_unit_price") AS "first_unit_price"
    FROM by_month_and_item
    GROUP BY by_month_and_item."category", by_month_and_item."name_and_unit_size"
    ORDER BY by_month_and_item."category", by_month_and_item."name_and_unit_size"
)
SELECT
    ROW_NUMBER() OVER () AS id,
    ap.*
FROM flatten ap
ORDER BY ap."category", ap."name_and_unit_size"


/*
select "inventory_rawitem"."name", "inventory_commonitemname"."name", "inventory_rawitem"."unit_quantity"
from "inventory_rawitem"
join "inventory_commonitemnamegroup"
on "inventory_rawitem"."common_item_name_group_id" = "inventory_commonitemnamegroup"."id"
join "inventory_commonitemname"
on "inventory_commonitemnamegroup"."name_id" = "inventory_commonitemname"."id"
where "inventory_rawitem"."unit_quantity" > 1
order by "inventory_commonitemname"."name", "inventory_rawitem"."name", "inventory_rawitem"."unit_quantity";
 */