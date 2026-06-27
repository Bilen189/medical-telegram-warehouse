{{ config(materialized='view') }}

select
    cast(message_id as integer) as message_id,
    channel_name,
    cast(message_date as timestamp) as message_timestamp,
    cast(message_date as date) as message_date,
    message_text,
    length(coalesce(message_text, '')) as message_length,
    cast(has_media as boolean) as has_media,
    case
        when image_path is not null then true
        else false
    end as has_image,
    image_path,
    cast(views as integer) as view_count,
    cast(forwards as integer) as forward_count,
    source_file
from raw.telegram_messages
where message_id is not null