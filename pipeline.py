import subprocess
from dagster import Definitions, ScheduleDefinition, job, op


@op
def scrape_telegram_data():
    subprocess.run(["python", "src/scraper.py"], check=True)
    return "scraping_complete"


@op
def load_raw_to_postgres(previous_step):
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


@job
def medical_telegram_pipeline():
    scraped = scrape_telegram_data()
    loaded = load_raw_to_postgres(scraped)
    transformed = run_dbt_transformations(loaded)
    yolo_done = run_yolo_enrichment(transformed)
    load_yolo_to_postgres(yolo_done)


daily_schedule = ScheduleDefinition(
    job=medical_telegram_pipeline,
    cron_schedule="0 1 * * *",
)

defs = Definitions(
    jobs=[medical_telegram_pipeline],
    schedules=[daily_schedule],
)  