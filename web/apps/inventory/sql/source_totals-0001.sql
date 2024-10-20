CREATE OR REPLACE FUNCTION source_totals(start_date DATE, end_date DATE)
RETURNS TABLE(delivered_year INT, iname VARCHAR, orders INT, items INT, total_cost NUMERIC(10,4)) AS
$$
    select
        DATE_PART('year', delivered_date) AS delivered_year,
        initcap(name) as iname,
        count(distinct format('%s|%s|%s', inv_s.name, inv_si.delivered_date, inv_si.order_number)) as orders,
        count(1) as items,
        round(sum(inv_si.extended_cost), 2) as total_cost
    from inventory_source as inv_s
    join inventory_sourceitem as inv_si
    on inv_s.id = inv_si.source_id
    where delivered_date >= start_date and delivered_date < end_date
    group by delivered_year, iname
    order by delivered_year, iname;
$$
LANGUAGE SQL;