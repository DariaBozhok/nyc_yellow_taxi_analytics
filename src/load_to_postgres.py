import pandas as pd
from sqlalchemy import create_engine

# Keep and rename only the columns fact_trips expects
fact = clean.rename(columns={
    "VendorID": "vendor_id",
    "tpep_pickup_datetime": "pickup_datetime",
    "tpep_dropoff_datetime": "dropoff_datetime",
    "PULocationID": "pu_location_id",
    "DOLocationID": "do_location_id",
})[[
    "vendor_id", "pickup_datetime", "dropoff_datetime", "passenger_count",
    "trip_distance", "pu_location_id", "do_location_id", "payment_type",
    "RatecodeID", "fare_amount", "tip_amount", "tolls_amount",
    "total_amount", "trip_duration_min",
]].rename(columns={"RatecodeID": "ratecode_id"})

print("Columns ready:", list(fact.columns))
print("Rows to load:", len(fact))

print("payment_type unique:", sorted(fact["payment_type"].dropna().unique()))
print("ratecode_id unique:", sorted(fact["ratecode_id"].dropna().unique()))
print("vendor_id unique:", sorted(fact["vendor_id"].dropna().unique()))
print()
print("ratecode_id NaN count:", fact["ratecode_id"].isna().sum())
print("passenger_count NaN count:", fact["passenger_count"].isna().sum())

from sqlalchemy import create_engine

# Connection: postgresql://user:password@host:port/database
# Default user is usually 'postgres'. Put YOUR password and DB name.
engine = create_engine(
    "postgresql+psycopg2://postgres:postgres@localhost:5432/Yellow Taxi"
)

# Load in chunks so memory stays low and we can see progress
fact.to_sql(
    "fact_trips",
    engine,
    if_exists="append",   # add rows to the existing table (don't recreate)
    index=False,          # don't write the pandas index
    chunksize=50000,      # 50k rows per batch
    method="multi",       # pack many rows into one INSERT (faster)
)

print("Done loading!")