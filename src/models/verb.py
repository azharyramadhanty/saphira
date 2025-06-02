from datetime import date
from sqlmodel import Field
from src.database.base import Base


class Verb(Base, table=True):
    __table_args__ = {"schema": "public"}

    verb_id: str = Field(primary_key=True, max_length=20)
    created_date: date | None = None
    changed_date: date | None = None
    verb_tag: str | None = None  # The tag used for search
    # Text for full-text search index (if you use one in DB)
    # tsvector not directly supported, you may handle this with raw SQL
    verb_token: str | None = None
