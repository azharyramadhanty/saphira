from datetime import date
from sqlmodel import Field
from src.database.base import Base


class Faq(Base, table=True):
    __table_args__ = {"schema": "public"}

    id: str = Field(primary_key=True, max_length=40)
    client_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.client.client_id")
    faq_id: str | None = Field(default=None, max_length=5)
    object_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.object.object_id")
    verb_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.verb.verb_id")
    question_text: str | None = None
    answer_text: str | None = None
    url: str | None = None
    created_date: date | None = None
    changed_date: date | None = None
    additional_tag: str | None = None
    # tsvector, store as string or use raw SQL for full-text
    additional_token: str | None = None
