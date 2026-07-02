-- Vendor dimension
CREATE TABLE dim_vendor (
    vendor_id   INTEGER PRIMARY KEY,
    vendor_name TEXT NOT NULL
);

INSERT INTO dim_vendor (vendor_id, vendor_name) VALUES
    (1, 'Creative Mobile Technologies'),
    (2, 'Curb Mobility'),
    (6, 'Myle Technologies'),
    (7, 'Helix');

-- Payment type dimension (0 = Unknown, used by ~25% of rows)
CREATE TABLE dim_payment (
    payment_type INTEGER PRIMARY KEY,
    payment_desc TEXT NOT NULL
);

INSERT INTO dim_payment (payment_type, payment_desc) VALUES
    (0, 'Unknown'),
    (1, 'Credit card'),
    (2, 'Cash'),
    (3, 'No charge'),
    (4, 'Dispute'),
    (5, 'Unknown'),
    (6, 'Voided trip');

-- Rate code dimension (99 = Unknown)
CREATE TABLE dim_ratecode (
    ratecode_id   INTEGER PRIMARY KEY,
    ratecode_desc TEXT NOT NULL
);

INSERT INTO dim_ratecode (ratecode_id, ratecode_desc) VALUES
    (1, 'Standard rate'),
    (2, 'JFK'),
    (3, 'Newark'),
    (4, 'Nassau/Westchester'),
    (5, 'Negotiated fare'),
    (6, 'Group ride'),
    (99, 'Unknown');

-- Zone dimension (loaded from taxi_zone_lookup.csv — see 02_load.sql)
CREATE TABLE dim_zone (
    location_id   INTEGER PRIMARY KEY,
    borough       TEXT,
    zone          TEXT,
    service_zone  TEXT
);

-- Fact table: one row per trip
CREATE TABLE fact_trips (
    trip_id            BIGSERIAL PRIMARY KEY,
    vendor_id          INTEGER REFERENCES dim_vendor(vendor_id),
    pickup_datetime    TIMESTAMP NOT NULL,
    dropoff_datetime   TIMESTAMP NOT NULL,
    passenger_count    INTEGER,
    trip_distance      NUMERIC(8,2) NOT NULL,
    pu_location_id     INTEGER REFERENCES dim_zone(location_id),
    do_location_id     INTEGER REFERENCES dim_zone(location_id),
    payment_type       INTEGER REFERENCES dim_payment(payment_type),
    ratecode_id        INTEGER REFERENCES dim_ratecode(ratecode_id),
    fare_amount        NUMERIC(10,2) NOT NULL,
    tip_amount         NUMERIC(10,2),
    tolls_amount       NUMERIC(10,2),
    total_amount       NUMERIC(10,2) NOT NULL,
    trip_duration_min  NUMERIC(8,2) NOT NULL,
    CONSTRAINT chk_positive_money CHECK (total_amount > 0 AND fare_amount >= 0),
    CONSTRAINT chk_distance       CHECK (trip_distance > 0),
    CONSTRAINT chk_duration       CHECK (trip_duration_min > 0)
);