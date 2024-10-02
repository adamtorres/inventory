CREATE OR REPLACE FUNCTION common_name_prices(start_date DATE, end_date DATE)
RETURNS TABLE(
    source_item_names VARCHAR, common_name VARCHAR, pack_quantity INT, unit_size VARCHAR, unit_quantity INT,
    first_delivered_date DATE, first_pack_cost NUMERIC(10,4),
    last_delivered_date DATE, last_pack_cost NUMERIC(10,4),
    cost_change NUMERIC(10,4), order_count INT, total_extended_cost NUMERIC(10,4)
    ) AS
$$
WITH data AS (
    SELECT
        CASE WHEN verbose_name = '' THEN cryptic_name ELSE verbose_name END AS source_item_name,
        INITCAP(source_category) AS category,
        INITCAP(common_name) AS fixed_common_name,
        *
    FROM source_orders(start_date, end_date) as orders
    JOIN inventory_sourceitem inv_si
        USING (source_id, delivered_date, order_number)
    WHERE lower(common_name) != 'dni'
)
, first_last AS (
    SELECT DISTINCT
        fixed_common_name, pack_quantity, unit_size, unit_quantity,
        FIRST_VALUE(order_number) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_order_number,
        FIRST_VALUE(delivered_date) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_delivered_date,
        FIRST_VALUE(pack_quantity) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_pack_quantity,
        FIRST_VALUE(unit_size) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_unit_size,
        FIRST_VALUE(unit_quantity) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_unit_quantity,
        FIRST_VALUE(pack_cost) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_pack_cost,
        FIRST_VALUE(extended_cost) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_extended_cost,

        FIRST_VALUE(order_number) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_order_number,
        FIRST_VALUE(delivered_date) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_delivered_date,
        FIRST_VALUE(pack_quantity) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_pack_quantity,
        FIRST_VALUE(unit_size) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_unit_size,
        FIRST_VALUE(unit_quantity) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_unit_quantity,
        FIRST_VALUE(pack_cost) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_pack_cost,
        FIRST_VALUE(extended_cost) OVER(PARTITION BY fixed_common_name, pack_quantity, unit_size, unit_quantity ORDER BY fixed_common_name, pack_quantity, unit_size, unit_quantity, delivered_date DESC RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_extended_cost
    FROM data
    ORDER BY fixed_common_name
)
, grouping AS (
    SELECT
        fixed_common_name, pack_quantity, unit_size, unit_quantity,
        STRING_AGG(DISTINCT source_item_name, E'\n') AS source_item_names,
        --ARRAY_AGG(DISTINCT unit_size) AS unit_sizes,
        SUM(extended_cost) AS total_extended_cost,
        COUNT(FORMAT('%s|%s|%s', delivered_date, source_name, order_number)) AS order_count
    FROM data
    WHERE fixed_common_name != ''
    GROUP BY fixed_common_name, pack_quantity, unit_size, unit_quantity
)
, final AS (
    SELECT
        g.source_item_names, g.fixed_common_name as common_name, g.pack_quantity, g.unit_size, g.unit_quantity,
        fl.first_delivered_date,
        fl.first_pack_cost,

        fl.last_delivered_date,
        fl.last_pack_cost,

        fl.last_pack_cost - fl.first_pack_cost AS cost_change,
        g.order_count,
        g.total_extended_cost
    FROM grouping g
    JOIN first_last fl
        USING (fixed_common_name, pack_quantity, unit_size, unit_quantity)
    ORDER BY g.fixed_common_name, fl.last_delivered_date DESC
)
SELECT *
FROM final
ORDER BY common_name;
$$
LANGUAGE SQL;
