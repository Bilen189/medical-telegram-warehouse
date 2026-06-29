from pydantic import BaseModel
from typing import Optional


class TopProduct(BaseModel):
    product_term: str
    mention_count: int


class ChannelActivity(BaseModel):
    message_date: str
    post_count: int
    total_views: Optional[int]


class MessageSearchResult(BaseModel):
    message_id: int
    channel_name: str
    message_text: Optional[str]
    view_count: Optional[int]


class VisualContentStats(BaseModel):
    channel_name: str
    image_category: str
    image_count: int