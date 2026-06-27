import json
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw" / "telegram_messages"

DB_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5432/medical_warehouse"


def load_json_files():
    records = []

    for file_path in RAW_DIR.rglob("*.json"):
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for row in data:
            row["source_file"] = str(file_path)
            records.append(row)

    return records


def main():
    records = load_json_files()

    if not records:
        raise ValueError("No JSON records found in data/raw/telegram_messages")

    df = pd.DataFrame(records)

    engine = create_engine(DB_URL)

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS raw"))

    df.to_sql(
        "telegram_messages",
        engine,
        schema="raw",
        if_exists="replace",
        index=False,
    )

    print(f"Loaded {len(df)} records into raw.telegram_messages")


if __name__ == "__main__":
    main()