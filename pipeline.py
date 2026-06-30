import subprocess
from dagster import Definitions, ScheduleDefinition, job, op


@op(description="Scrape Telegram messages and images into the raw data lake.")
def scrape_telegram_data():
    subprocess.run(["python", "src/scraper.py"], check=True)
    return "scraping_complete"


@op(description="Load raw Telegram JSON data into PostgreSQL.")
def load_raw_to_postgres(previous_step):
    subprocess.run(["python", "scripts/load_raw_to_postgres.py"], check=True)
    return "raw_load_complete"


@op(description="Run dbt models and data quality tests.")
def run_dbt_transformations(previous_step):
    subprocess.run(["dbt", "run"], cwd="medical_warehouse", check=True)
    subprocess.run(["dbt", "test"], cwd="medical_warehouse", check=True)
    return "dbt_complete"


@op(description="Run YOLOv8 object detection on downloaded Telegram images.")
def run_yolo_enrichment(previous_step):
    subprocess.run(["python", "src/yolo_detect.py"], check=True)
    return "yolo_complete"


@op(description="Load YOLO image detection results into PostgreSQL.")
def load_yolo_to_postgres(previous_step):
    subprocess.run(["python", "scripts/load_detections_to_postgres.py"], check=True)
    return "yolo_load_complete"


@op(description="Refresh dbt models after YOLO enrichment.")
def refresh_dbt_after_yolo(previous_step):
    subprocess.run(["dbt", "run"], cwd="medical_warehouse", check=True)
    subprocess.run(["dbt", "test"], cwd="medical_warehouse", check=True)
    return "pipeline_complete"


@job(description="End-to-end Telegram medical data pipeline orchestrated with Dagster.")
def medical_telegram_pipeline():
    scraped = scrape_telegram_data()
    raw_loaded = load_raw_to_postgres(scraped)
    dbt_done = run_dbt_transformations(raw_loaded)
    yolo_done = run_yolo_enrichment(dbt_done)
    yolo_loaded = load_yolo_to_postgres(yolo_done)
    refresh_dbt_after_yolo(yolo_loaded)


daily_schedule = ScheduleDefinition(
    job=medical_telegram_pipeline,
    cron_schedule="0 1 * * *",
)

defs = Definitions(
    jobs=[medical_telegram_pipeline],
    schedules=[daily_schedule],
)