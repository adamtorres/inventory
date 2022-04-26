SELECT
    ((CURRENT_TIMESTAMP - FORMAT('12 months %s days', EXTRACT('days' FROM CURRENT_TIMESTAMP)-1)::INTERVAL)::DATE)::TIMESTAMP WITH TIME ZONE AS p_startdate,
    CURRENT_TIMESTAMP AS p_enddate,
    '{"butter", "ground beef", "corn", "cut green beans", "smoked boneless pit ham", "hamburger sesame buns", "sweetener packets", "semi sweet chocolate chips", "flour"}' AS p_selected_items
\gset

SELECT *
FROM f_item_price_history(:'p_startdate', :'p_enddate', :'p_selected_items')
ORDER BY category, name_and_unit_size;
