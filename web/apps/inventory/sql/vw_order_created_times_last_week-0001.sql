CREATE OR REPLACE VIEW public.vw_order_created_times_last_week
AS
select date_trunc('hour', created AT TIME ZONE 'MDT') as created_trunc,
       COUNT(distinct format('%s|%s|%s', delivered_date, source_id, order_number)) as orders,
       COUNT(1) as items,
       MIN(created AT TIME ZONE 'MDT') as first_created,
       MAX(created AT TIME ZONE 'MDT') as last_created,
       round(extract(epoch from max(created) - min(created)) / 3600, 4) as est_hours
from inventory_sourceitem
WHERE (EXTRACT(epoch FROM created - CURRENT_TIMESTAMP) / 3600::numeric) >= (-24)*7
group by created_trunc
order by created_trunc;
