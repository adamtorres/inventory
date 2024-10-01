CREATE OR REPLACE FUNCTION public.source_orders_first_and_last(start_date DATE, end_date DATE)
    RETURNS TABLE(source_id UUID, source_name VARCHAR, first_order_number VARCHAR, first_delivered_date DATE, last_order_number VARCHAR, last_delivered_date DATE)
AS
$$
SELECT DISTINCT
    orders.source_id, orders.source_name,
    FIRST_VALUE(inv_si.order_number) OVER(PARTITION BY orders.source_name ORDER BY orders.source_name, inv_si.delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_order_number,
    FIRST_VALUE(inv_si.delivered_date) OVER(PARTITION BY orders.source_name ORDER BY orders.source_name, inv_si.delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS first_delivered_date,
    LAST_VALUE(inv_si.order_number) OVER(PARTITION BY orders.source_name ORDER BY orders.source_name, inv_si.delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_order_number,
    LAST_VALUE(inv_si.delivered_date) OVER(PARTITION BY orders.source_name ORDER BY orders.source_name, inv_si.delivered_date RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS last_delivered_date
FROM source_orders(start_date, end_date) as orders
JOIN inventory_sourceitem inv_si
    USING (source_id, delivered_date, order_number)
ORDER BY orders.source_name, orders.source_id
$$
LANGUAGE SQL;
