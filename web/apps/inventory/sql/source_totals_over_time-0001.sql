CREATE OR REPLACE FUNCTION source_totals_over_time(start_date DATE, end_date DATE)
RETURNS TABLE(year_month VARCHAR, iname VARCHAR, orders INT, items INT, total_cost NUMERIC(10,4)) AS
$$
with raw as (
    select
        to_char(date_trunc('month', inv_si.delivered_date), 'YYYY-MM') as year_month,
        initcap(name) as iname,
        count(distinct format('%s|%s|%s', inv_s.name, inv_si.delivered_date, inv_si.order_number)) as orders,
        count(1) as items,
        round(sum(inv_si.extended_cost), 2) as total_cost
    from inventory_source as inv_s
    join inventory_sourceitem as inv_si
    on inv_s.id = inv_si.source_id
    where delivered_date >= start_date and delivered_date < end_date
    group by year_month, iname
    order by year_month, iname
),
date_range as (
    SELECT to_char(x, 'YYYY-MM') as year_month
    FROM generate_series(
        date_trunc('month', start_date::DATE),
        date_trunc('month', end_date::DATE - '1 day'::INTERVAL),
        '1 month'::INTERVAL) x
),
source_names as (
    SELECT DISTINCT iname
    FROM raw
),
zeros as (
    SELECT year_month, iname, 0 as orders, 0 as items, 0::NUMERIC(10,4) as total_cost
    FROM date_range, source_names
    ORDER BY year_month, iname
)
SELECT
    zeros.year_month, zeros.iname,
    COALESCE(raw.orders, zeros.orders) as orders,
    COALESCE(raw.items, zeros.items) as items,
    COALESCE(raw.total_cost, zeros.total_cost) as total_cost
FROM zeros
LEFT JOIN raw
USING (year_month, iname)
ORDER BY zeros.year_month, zeros.iname;
$$
LANGUAGE SQL;