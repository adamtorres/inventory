show_dupes_sql = """
select date_trunc('day', created) as day, count(1)
from inventory_sourceitem
where order_number = '585127305'
group by day
order by day;
"""

delete_sql = """
delete from inventory_sourceitem
where order_number = '585127305' and date_trunc('day', created) = '2023-09-09';
"""
