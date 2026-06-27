{{ config(materialized='table') }}

select
    row_number() over (order by channel_name) as channel_key,
    channel_name,
    case
        when channel_name ilike '%lobelia%' then 'Cosmetics'
        when channel_name ilike '%tikvah%' then 'Pharmaceutical'
        when channel_name ilike '%chemed%' then 'Medical'
        else 'Medical'
    end as channel_type,
    min(message_date) as first_post_date,
    max(message_date) as last_post_date,
    count(*) as total_posts,
    avg(view_count) as avg_views
from {{ ref('stg_telegram_messages') }}
group by channel_name