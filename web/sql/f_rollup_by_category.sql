-- gset ending a query will store the results into variables using the names of the fields.
SELECT
    ((CURRENT_TIMESTAMP - FORMAT('3 months %s days', EXTRACT('days' FROM CURRENT_TIMESTAMP)-1)::INTERVAL)::DATE)::TIMESTAMP WITH TIME ZONE AS p_startdate,
    CURRENT_TIMESTAMP AS p_enddate
\gset

WITH line_items AS (
    SELECT
        "inventory_category"."name" AS "category",
        "inventory_commonitemname"."name",
        "inventory_rawitem"."unit_size",
        FORMAT(
            '%s;%s;%s',
            "inventory_rawincomingitem"."source",
            "inventory_rawincomingitem"."order_number",
            "inventory_rawincomingitem"."delivery_date"
        ) AS "order_key",
        "inventory_rawincomingitem"."delivered_quantity",
        "inventory_rawitem"."pack_quantity",
        "inventory_rawincomingitem"."extended_price",
        "inventory_rawincomingitem"."delivery_date"
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
),
by_category AS (
    SELECT
        line_items."category",
        SUM(line_items."extended_price") AS "extended_price",
        COUNT(DISTINCT line_items."order_key") AS "orders"
    FROM line_items
    GROUP BY line_items."category"
),
add_percents AS (
    SELECT
        bc.*,
        ROUND(bc."extended_price" / SUM(bc."extended_price") OVER w, 4) AS percent_of_total_price,
        ROUND(bc."orders" / SUM(bc."orders") OVER w, 4) AS percent_of_total_orders
    FROM by_category bc
    WINDOW w AS (
        ORDER BY bc."category"
        RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    )
)
SELECT
    ROW_NUMBER() OVER () AS id,
    ap.*
FROM add_percents ap
ORDER BY ap."category";