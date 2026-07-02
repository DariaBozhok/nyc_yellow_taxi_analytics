import pandas as pd

folder = "/Users/dariabozok/Desktop/Yellow Taxi"

df_01 = pd.read_parquet(f"{folder}/yellow_tripdata_2026-01.parquet")
df_02 = pd.read_parquet(f"{folder}/yellow_tripdata_2026-02.parquet")
df_03 = pd.read_parquet(f"{folder}/yellow_tripdata_2026-03.parquet")
df_04 = pd.read_parquet(f"{folder}/yellow_tripdata_2026-04.parquet")
df_05 = pd.read_parquet(f"{folder}/yellow_tripdata_2026-05.parquet")

df = pd.concat([df_01, df_02, df_03, df_04, df_05], ignore_index=True)

print("Shape:", df.shape)
print()
print("Columns and types:")
print(df.dtypes)
print()
print("First rows:")
print(df.head())

print("Missing values per column:")
print(df.isna().sum())
print()
print("Missing values (%):")
print((df.isna().sum() / len(df) * 100).round(1))

# Mask: rows where passenger_count is missing
mask = df["passenger_count"].isna()

# In those rows, are the other four columns also always missing?
print("Rows with missing passenger_count:", mask.sum())
print()
print("Of those, how many also miss the other columns:")
print("RatecodeID:", df.loc[mask, "RatecodeID"].isna().sum())
print("store_and_fwd_flag:", df.loc[mask, "store_and_fwd_flag"].isna().sum())
print("congestion_surcharge:", df.loc[mask, "congestion_surcharge"].isna().sum())
print("Airport_fee:", df.loc[mask, "Airport_fee"].isna().sum())
print()
# Are the financial fields still valid in those rows?
print("Financial fields in those rows (should be valid):")
print(df.loc[mask, ["fare_amount", "total_amount", "trip_distance"]].describe())

print("fare_amount:")
print(df["fare_amount"].describe())
print()
print("total_amount:")
print(df["total_amount"].describe())
print()
print("trip_distance:")
print(df["trip_distance"].describe())
print()
# Duration in minutes (we compute it from the two timestamps)
duration = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60
print("trip_duration_min:")
print(duration.describe())

duration = (df["tpep_dropoff_datetime"] - df["tpep_pickup_datetime"]).dt.total_seconds() / 60

print("Bad money (total<=0 or fare<0):", ((df["total_amount"] <= 0) | (df["fare_amount"] < 0)).sum())
print("Distance = 0:", (df["trip_distance"] == 0).sum())
print("Distance > 100 miles:", (df["trip_distance"] > 100).sum())
print("Duration <= 0:", (duration <= 0).sum())
print("Duration > 180 min:", (duration > 180).sum())

# Work on a copy so the original df stays intact
clean = df.copy()

# Add trip duration in minutes as a real column
clean["trip_duration_min"] = (
    clean["tpep_dropoff_datetime"] - clean["tpep_pickup_datetime"]
).dt.total_seconds() / 60

print("Before cleaning:", len(clean))

# Keep only pickups within our data window (Jan–May 2026)
start = pd.Timestamp("2026-01-01")
end = pd.Timestamp("2026-06-01")

mask_date = (clean["tpep_pickup_datetime"] >= start) & (clean["tpep_pickup_datetime"] < end)

print("Rows failing date check:", (~mask_date).sum())
clean = clean[mask_date]
print("After date filter:", len(clean))

# Money must be valid: total > 0 and fare >= 0
mask_money = (clean["total_amount"] > 0) & (clean["fare_amount"] >= 0)
print("Rows failing money check:", (~mask_money).sum())
clean = clean[mask_money]
print("After money filter:", len(clean))
print()

# Distance must be > 0 and not absurd (<= 100 miles)
mask_dist = (clean["trip_distance"] > 0) & (clean["trip_distance"] <= 100)
print("Rows failing distance check:", (~mask_dist).sum())
clean = clean[mask_dist]
print("After distance filter:", len(clean))
print()

# Duration must be > 0 and not absurd (<= 180 min)
mask_dur = (clean["trip_duration_min"] > 0) & (clean["trip_duration_min"] <= 180)
print("Rows failing duration check:", (~mask_dur).sum())
clean = clean[mask_dur]
print("After duration filter:", len(clean))

# passenger_count = 0 is not a real value -> mark as unknown (NA)
print("passenger_count = 0 before:", (clean["passenger_count"] == 0).sum())
clean.loc[clean["passenger_count"] == 0, "passenger_count"] = pd.NA
print("passenger_count = 0 after:", (clean["passenger_count"] == 0).sum())

print("Duplicate rows:", clean.duplicated().sum())

# Save cleaned data so we don't rerun cleaning every time
output_path = "/Users/dariabozok/Desktop/Yellow Taxi/clean_taxi.parquet"
clean.to_parquet(output_path, index=False)

print("Saved:", output_path)
print("Final shape:", clean.shape)

clean = pd.read_parquet("/Users/dariabozok/Desktop/Yellow Taxi/clean_taxi.parquet")

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