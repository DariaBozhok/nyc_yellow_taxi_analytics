import pandas as pd
from sqlalchemy import create_engine

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