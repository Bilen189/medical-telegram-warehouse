## Dagster Pipeline

The project includes a Dagster orchestration pipeline that automates the end-to-end workflow.

Pipeline steps:

1. Load raw Telegram data into PostgreSQL.
2. Execute dbt transformations and data quality tests.
3. Run YOLOv8 object detection on downloaded images.
4. Load image detections into PostgreSQL.
5. Refresh dbt models after image enrichment.

The pipeline also includes a daily schedule configured using Dagster.