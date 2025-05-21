# scripts/collect_demand_historical.py

import os
import requests
import pandas as pd
from datetime import datetime, timedelta
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

# CONFIG
TOKEN = os.getenv("API_TOKEN")
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Token token={TOKEN}"
}
INDICATOR_ID = 600  # Real-time demand
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime.now().date()

# CREATE FOLDERS
os.makedirs("database/demand_csv", exist_ok=True)
os.makedirs("database/demand_parquet", exist_ok=True)
os.makedirs("database/demand_duckdb", exist_ok=True)

# CONNECT TO DUCKDB
con = duckdb.connect("database/demand_duckdb/demand_data.duckdb")
first_insert = True

# MAIN LOOP
current_date = START_DATE
while current_date <= END_DATE:
    date_str = current_date.strftime("%Y-%m-%d")

    csv_path = f"database/demand_csv/{date_str}-hourly.csv"
    parquet_path = f"database/demand_parquet/{date_str}-hourly.parquet"

    if os.path.exists(csv_path):
        print(f"Skipping existing: {csv_path}")
        current_date += timedelta(days=1)
        continue

    print(f"Fetching {date_str}...")

    start_utc = current_date.strftime("%Y-%m-%dT00:00:00Z")
    end_utc = current_date.strftime("%Y-%m-%dT23:59:59Z")

    url = f"https://api.esios.ree.es/indicators/{INDICATOR_ID}?start_date={start_utc}&end_date={end_utc}&time_trunc=hour"

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data['indicator']['values'])

        if df.empty:
            print(f"No data for {date_str}, skipping.")
        else:
            # Save CSV
            df.to_csv(csv_path, index=False)

            # Save Parquet
            table = pa.Table.from_pandas(df)
            pq.write_table(table, parquet_path)

            # Append to DuckDB
            if first_insert:
                con.execute("CREATE TABLE IF NOT EXISTS demand AS SELECT * FROM df LIMIT 0")
                first_insert = False
            con.execute("INSERT INTO demand SELECT * FROM df")

            print(f"Saved {date_str} to all formats.")
    except Exception as e:
        print(f"Failed to fetch {date_str}: {e}")

    current_date += timedelta(days=1)

con.close()
print("Done.")
