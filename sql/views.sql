
-- NYC Yellow Taxi — Analytical Views

-- Daily aggregated statistics (with month for filtering)
CREATE VIEW v_daily_agg AS
SELECT
    pickup_datetime::date                    AS trip_date,
    EXTRACT(MONTH FROM pickup_datetime)::int AS trip_month,
    COUNT(*)                                 AS total_trips,
    ROUND(AVG(trip_distance), 2)             AS avg_distance,
    ROUND(AVG(trip_duration_min), 2)         AS avg_duration,
    ROUND(AVG(fare_amount), 2)               AS avg_fare,
    ROUND(SUM(total_amount), 2)              AS total_revenue,
    ROUND(AVG(tip_amount), 2)                AS avg_tip
FROM fact_trips
GROUP BY trip_date, trip_month
ORDER BY trip_date;

-- Hourly profile by month and hour of day
CREATE VIEW v_hourly AS
SELECT
    EXTRACT(MONTH FROM pickup_datetime)::int AS trip_month,
    EXTRACT(HOUR FROM pickup_datetime)::int  AS pickup_hour,
    COUNT(*)                                 AS total_trips,
    ROUND(AVG(fare_amount), 2)               AS avg_fare,
    ROUND(AVG(tip_amount), 2)                AS avg_tip
FROM fact_trips
GROUP BY trip_month, pickup_hour
ORDER BY trip_month, pickup_hour;

-- Zone statistics by month (with location_id for map join)
CREATE VIEW v_zone_stats AS
SELECT
    EXTRACT(MONTH FROM f.pickup_datetime)::int AS trip_month,
    z.location_id,
    z.borough,
    z.zone,
    COUNT(*)                                   AS total_trips,
    ROUND(AVG(f.trip_distance), 2)             AS avg_distance,
    ROUND(AVG(f.fare_amount), 2)               AS avg_fare,
    ROUND(SUM(f.total_amount), 2)              AS total_revenue
FROM fact_trips f
JOIN dim_zone z ON f.pu_location_id = z.location_id
GROUP BY trip_month, z.location_id, z.borough, z.zone
ORDER BY trip_month, total_trips DESC;

-- Validation queries (run manually to verify)

-- SELECT COUNT(*) FROM fact_trips;
-- SELECT COUNT(*) FROM dim_zone;
-- SELECT * FROM v_daily_agg LIMIT 10;
-- SELECT * FROM v_hourly LIMIT 10;
-- SELECT * FROM v_zone_stats LIMIT 10;