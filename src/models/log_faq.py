from datetime import date, time
from sqlalchemy import Column, Date, Time
from sqlmodel import Field
from src.database.base import Base
from src.utils.db_utils import current_utc_date, current_utc_time


class LogFaq(Base, table=True):
    __table_args__ = {"schema": "public"}

    # Auto-incrementing primary key
    id: int | None = Field(default=None, primary_key=True)
    session_id: str | None = Field(default=None, max_length=255)
    log_date: date = Field(default_factory=current_utc_date,
                           sa_column=Column("date", Date))
    log_time: time = Field(default_factory=current_utc_time,
                           sa_column=Column("time", Time))
    email: str | None = Field(default=None, max_length=240)
    client_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.client.client_id")
    question: str | None = Field(default=None)
    faq_id: str | None = Field(
        default=None, max_length=5, foreign_key="public.faq.faq_id")
    faq_feedback: str | None = Field(default=None, max_length=3)
    stream: str | None = Field(default=None, max_length=40)
    sub_stream: str | None = Field(default=None, max_length=40)
    object_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.object.object_id")
    verb_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.verb.verb_id")
