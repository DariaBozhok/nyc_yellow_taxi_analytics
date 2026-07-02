import pandas as pd
from sqlalchemy import create_engine

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