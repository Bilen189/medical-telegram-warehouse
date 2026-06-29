{{ config(materialized='table') }}

select
    row_number() over (
        order by d.message_id, d.detected_class, d.confidence_score desc
    ) as detection_key,
    d.message_id,
    m.channel_key,
    m.date_key,
    d.channel_name,
    d.image_path,
    d.detected_class,
    d.confidence_score,
    d.image_category
from {{ ref('stg_image_detections') }} d
left join {{ ref('fct_messages') }} m
    on d.message_id = m.message_id