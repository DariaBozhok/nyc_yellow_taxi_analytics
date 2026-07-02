-- -- Vendor dimension
-- CREATE TABLE dim_vendor (
--     vendor_id   INTEGER PRIMARY KEY,
--     vendor_name TEXT NOT NULL
-- );

-- INSERT INTO dim_vendor (vendor_id, vendor_name) VALUES
--     (1, 'Creative Mobile Technologies'),
--     (2, 'Curb Mobility'),
--     (6, 'Myle Technologies'),
--     (7, 'Helix');

-- -- Payment type dimension (0 = Unknown, used by ~25% of rows)
-- CREATE TABLE dim_payment (
--     payment_type INTEGER PRIMARY KEY,
--     payment_desc TEXT NOT NULL
-- );

-- INSERT INTO dim_payment (payment_type, payment_desc) VALUES
--     (0, 'Unknown'),
--     (1, 'Credit card'),
--     (2, 'Cash'),
--     (3, 'No charge'),
--     (4, 'Dispute'),
--     (5, 'Unknown'),
--     (6, 'Voided trip');

-- -- Rate code dimension (99 = Unknown)
-- CREATE TABLE dim_ratecode (
--     ratecode_id   INTEGER PRIMARY KEY,
--     ratecode_desc TEXT NOT NULL
-- );

-- INSERT INTO dim_ratecode (ratecode_id, ratecode_desc) VALUES
--     (1, 'Standard rate'),
--     (2, 'JFK'),
--     (3, 'Newark'),
--     (4, 'Nassau/Westchester'),
--     (5, 'Negotiated fare'),
--     (6, 'Group ride'),
--     (99, 'Unknown');

-- CREATE TABLE dim_zone (
--     location_id   INTEGER PRIMARY KEY,
--     borough       TEXT,
--     zone          TEXT,
--     service_zone  TEXT
-- );

-- SELECT COUNT(*) FROM dim_zone;
-- SELECT * FROM dim_zone ORDER BY location_id LIMIT 10;

-- CREATE TABLE fact_trips (
--     trip_id            BIGSERIAL PRIMARY KEY,
--     vendor_id          INTEGER REFERENCES dim_vendor(vendor_id),
--     pickup_datetime    TIMESTAMP NOT NULL,
--     dropoff_datetime   TIMESTAMP NOT NULL,
--     passenger_count    INTEGER,
--     trip_distance      NUMERIC(8,2) NOT NULL,
--     pu_location_id     INTEGER REFERENCES dim_zone(location_id),
--     do_location_id     INTEGER REFERENCES dim_zone(location_id),
--     payment_type       INTEGER REFERENCES dim_payment(payment_type),
--     ratecode_id        INTEGER REFERENCES dim_ratecode(ratecode_id),
--     fare_amount        NUMERIC(10,2) NOT NULL,
--     tip_amount         NUMERIC(10,2),
--     tolls_amount       NUMERIC(10,2),
--     total_amount       NUMERIC(10,2) NOT NULL,
--     trip_duration_min  NUMERIC(8,2) NOT NULL,
--     CONSTRAINT chk_positive_money CHECK (total_amount > 0 AND fare_amount >= 0),
--     CONSTRAINT chk_distance       CHECK (trip_distance > 0),
--     CONSTRAINT chk_duration       CHECK (trip_duration_min > 0)
-- );

-- -- 1. Total rows — should be 18,074,891
-- SELECT COUNT(*) FROM fact_trips;

-- -- 2. Check the star joins actually work (fact -> dimensions)
-- SELECT
--     p.payment_desc,
--     COUNT(*) AS trips
-- FROM fact_trips f
-- JOIN dim_payment p ON f.payment_type = p.payment_type
-- GROUP BY p.payment_desc
-- ORDER BY trips DESC;

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

-- SELECT COUNT(*) FROM fact_trips;
-- SELECT COUNT(*) FROM dim_zone;
-- SELECT * FROM v_daily_agg LIMIT 10;
-- SELECT * FROM v_hourly LIMIT 10;
-- SELECT * FROM v_zone_stats LIMIT 10;