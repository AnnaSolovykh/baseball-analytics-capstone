import sqlite3
import pandas as pd
import os

RAW_DIR = "data/raw"
DB_PATH = "data/baseball.db"

conn = sqlite3.connect(DB_PATH)

for filename in os.listdir(RAW_DIR):
    if filename.endswith(".csv"):
        file_path = os.path.join(RAW_DIR, filename)
        table_name = os.path.splitext(filename)[0]

        print(f"Importing: {filename} → table `{table_name}`")

        df = pd.read_csv(file_path)

        # Try to convert each column to numeric where possible
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass  # If it can't be converted, leave as-is

        df.to_sql(table_name, conn, if_exists="replace", index=False)

conn.close()
print("All CSV files have been imported into SQLite.")
