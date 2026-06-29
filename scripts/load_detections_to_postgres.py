import pandas as pd
from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5432/medical_warehouse"

engine = create_engine(DATABASE_URL)

df = pd.read_csv("data/processed/yolo_detections.csv")

df.to_sql(
    "image_detections",
    engine,
    schema="raw",
    if_exists="replace",
    index=False
)

print(f"Loaded {len(df)} detections into raw.image_detections")