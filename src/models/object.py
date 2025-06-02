from sqlmodel import Field
from datetime import date
from src.database.base import Base


class Object(Base, table=True):
    __table_args__ = {"schema": "public"}

    id: str = Field(primary_key=True, max_length=40)
    client_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.client.client_id")
    object_id: str | None = Field(default=None, max_length=20)
    stream: str | None = Field(default=None, max_length=40)
    sub_stream: str | None = Field(default=None, max_length=40)
    created_date: date | None = None
    changed_date: date | None = None
    object_tag: str | None = None  # The tag used for search
    # Text for full-text search index (if you use one in DB)
    # tsvector not directly supported, you may handle this with raw SQL
    object_token: str | None = None
