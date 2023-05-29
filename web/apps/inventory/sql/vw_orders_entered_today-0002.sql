CREATE OR REPLACE VIEW public.vw_orders_entered_today
AS
 WITH cte_orders_entered_today AS (
         SELECT DISTINCT inventory_sourceitem.order_number AS lo_order_number,
            inventory_sourceitem.delivered_date AS lo_delivered_date,
            inventory_sourceitem.source_id AS lo_source_id
           FROM inventory_sourceitem
          WHERE (EXTRACT(EPOCH FROM inventory_sourceitem.created - current_timestamp) / 3600) >= -24
        ), order_items AS (
         SELECT isi.order_number,
            isi.delivered_date,
            isi.item_code,
            isi.extra_code,
            isi.cryptic_name,
            isi.verbose_name,
            isi.common_name,
            isi.delivered_quantity,
            isi.pack_quantity,
            isi.unit_quantity,
            isi.unit_size,
            isi.total_weight,
            isi.individual_weights,
            isi.extra_notes,
            isi.scanned_filename,
            isi.extended_cost,
            isi.pack_cost,
            isi.created,
            isi.modified,
            isrc.name AS source_name,
			isi.source_id
           FROM inventory_sourceitem isi
             JOIN cte_orders_entered_today lo ON isi.order_number::text = lo.lo_order_number::text AND isi.delivered_date = lo.lo_delivered_date AND isi.source_id = lo.lo_source_id
             JOIN inventory_source isrc ON isi.source_id = isrc.id
        )
 SELECT order_items.delivered_date,
    order_items.source_name,
    order_items.order_number,
    count(1) AS line_items,
    sum(order_items.extended_cost) AS total_cost,
    min(order_items.created) AS created_min,
	extract(epoch from min(order_items.created) - current_timestamp) / 3600 as created_diff,
	order_items.source_id
   FROM order_items
  GROUP BY order_items.delivered_date, order_items.source_name, order_items.source_id, order_items.order_number
  ORDER BY (min(order_items.created)) DESC, order_items.delivered_date, order_items.order_number;
