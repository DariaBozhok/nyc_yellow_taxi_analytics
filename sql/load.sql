-- dim_zone:
--   Loaded from taxi_zone_lookup.csv (265 NYC zones)
--   via pgAdmin: right-click dim_zone -> Import/Export Data
--   Format: csv, Header: on, Delimiter: ','
--   265 rows expected.

-- fact_trips:
--   Loaded from Python (cleaned data, ~18.07M rows)
--   using pandas + SQLAlchemy (to_sql, chunksize=50000).
--   See src/load_to_postgres.py in the project.