CREATE OR REPLACE FUNCTION public.source_orders(start_date DATE, end_date DATE)
    RETURNS TABLE(source_id UUID, source_active BOOLEAN, source_name VARCHAR, delivered_date DATE, order_number VARCHAR, generated_order_number INTEGER, generated_reverse_order_number INTEGER)
AS
$$
SELECT
    inv_si.source_id, inv_s.active AS source_active, INITCAP(inv_s.name) AS source_name,
    inv_si.delivered_date, inv_si.order_number,
    ROW_NUMBER() OVER (PARTITION BY inv_si.source_id ORDER BY inv_si.source_id, inv_si.delivered_date, inv_si.order_number) as generated_order_number,
    ROW_NUMBER() OVER (PARTITION BY inv_si.source_id ORDER BY inv_si.source_id, inv_si.delivered_date DESC, inv_si.order_number DESC) as generated_reverse_order_number
FROM inventory_source AS inv_s
JOIN inventory_sourceitem AS inv_si
    ON inv_s.id = inv_si.source_id
WHERE delivered_date >= start_date AND delivered_date < end_date
GROUP BY
    inv_si.source_id, source_active, source_name,
    inv_si.delivered_date, inv_si.order_number
ORDER BY source_name, inv_si.delivered_date, inv_si.order_number
$$
LANGUAGE SQL;
