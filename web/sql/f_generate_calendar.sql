--A leap year
--SELECT full_date, day_part, month_part, year_part FROM generate_calendar('20040219'::date)

--Arbitrary common year
--SELECT full_date, day_part, month_part, year_part FROM generate_calendar('20050621'::date)

--Current year
--SELECT full_date, day_part, month_part, year_part FROM generate_calendar()

--Only year and months
--SELECT DISTINCT year_part, month_part FROM generate_calendar() ORDER BY year_part, month_part;

CREATE OR REPLACE FUNCTION generate_calendar(
    date DEFAULT NULL,
    OUT full_date timestamp with time zone, OUT day_part integer, OUT month_part integer, OUT year_part integer
) RETURNS SETOF RECORD AS
$$
    SELECT
        _full_date AS full_date,
        EXTRACT(DAY FROM _full_date)::INTEGER AS "day_part",
        EXTRACT(MONTH FROM _full_date)::INTEGER AS "month_part",
        EXTRACT(YEAR FROM _full_date)::INTEGER AS "year_part"
    FROM GENERATE_SERIES(
        DATE_TRUNC('year', COALESCE($1, CURRENT_DATE)),
        DATE_TRUNC('year', COALESCE($1, CURRENT_DATE)) + INTERVAL '1 year -1 day',
        '1 day'::INTERVAL) _full_date
$$
LANGUAGE SQL IMMUTABLE;

