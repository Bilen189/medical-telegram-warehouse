import subprocess
from dagster import Definitions, ScheduleDefinition, job, op


@op(description="Load raw Telegram messages into PostgreSQL.")
def load_raw_to_postgres():
    subprocess.run(["python", "scripts/load_raw_to_postgres.py"], check=True)
    return "raw_load_complete"


@op
def run_dbt_transformations(previous_step):
    subprocess.run(["dbt", "run"], cwd="medical_warehouse", check=True)
    subprocess.run(["dbt", "test"], cwd="medical_warehouse", check=True)
    return "dbt_complete"


@op
def run_yolo_enrichment(previous_step):
    subprocess.run(["python", "src/yolo_detect.py"], check=True)
    return "yolo_complete"


@op
def load_yolo_to_postgres(previous_step):
    subprocess.run(["python", "scripts/load_detections_to_postgres.py"], check=True)
    return "yolo_load_complete"


@op
def refresh_dbt_after_yolo(previous_step):
    subprocess.run(["dbt", "run"], cwd="medical_warehouse", check=True)
    subprocess.run(["dbt", "test"], cwd="medical_warehouse", check=True)
    return "pipeline_complete"


@job(
    description="End-to-end medical Telegram ETL pipeline orchestrated with Dagster."
)
def medical_telegram_pipeline():
    raw_loaded = load_raw_to_postgres()
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