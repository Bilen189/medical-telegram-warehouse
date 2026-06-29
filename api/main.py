from fastapi import Depends, FastAPI, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from api.database import get_db

app = FastAPI(
    title="Medical Telegram Warehouse API",
    description="Analytical API for Telegram medical business data.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {"message": "Medical Telegram Warehouse API is running"}


@app.get("/api/reports/top-products")
def get_top_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = text("""
        select
            lower(word) as product_term,
            count(*) as mention_count
        from (
            select regexp_split_to_table(message_text, '\\s+') as word
            from raw.fct_messages
            where message_text is not null
        ) words
        where length(word) > 3
        group by lower(word)
        order by mention_count desc
        limit :limit
    """)
    return db.execute(query, {"limit": limit}).mappings().all()


@app.get("/api/channels/{channel_name}/activity")
def get_channel_activity(
    channel_name: str,
    db: Session = Depends(get_db),
):
    query = text("""
        select
            d.full_date::text as message_date,
            count(*) as post_count,
            sum(m.view_count) as total_views
        from raw.fct_messages m
        join raw.dim_channels c on m.channel_key = c.channel_key
        join raw.dim_dates d on m.date_key = d.date_key
        where lower(c.channel_name) like lower(:channel_name)
        group by d.full_date
        order by d.full_date
    """)
    return db.execute(query, {"channel_name": f"%{channel_name}%"}).mappings().all()


@app.get("/api/search/messages")
def search_messages(
    query: str = Query(..., min_length=2),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    sql = text("""
        select
            m.message_id,
            c.channel_name,
            m.message_text,
            m.view_count
        from raw.fct_messages m
        join raw.dim_channels c on m.channel_key = c.channel_key
        where m.message_text ilike :query
        order by m.view_count desc nulls last
        limit :limit
    """)
    return db.execute(sql, {"query": f"%{query}%", "limit": limit}).mappings().all()


@app.get("/api/reports/visual-content")
def get_visual_content_stats(db: Session = Depends(get_db)):
    query = text("""
        select
            channel_name,
            image_category,
            count(*) as image_count
        from raw.fct_image_detections
        group by channel_name, image_category
        order by channel_name, image_count desc
    """)
    return db.execute(query).mappings().all()