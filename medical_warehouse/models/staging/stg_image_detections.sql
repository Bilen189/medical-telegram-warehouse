{{ config(materialized='view') }}

select
    cast(message_id as integer) as message_id,
    channel_name,
    image_path,
    detected_class,
    cast(confidence_score as numeric) as confidence_score,
    image_category
from raw.image_detections
where message_id is not null