from datetime import date, time
from sqlalchemy import Column, Date, Time
from sqlmodel import Field
from src.database.base import Base
from src.utils.db_utils import current_utc_date, current_utc_time


class Log(Base, table=True):
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
    dialog_id: str | None = Field(default=None, max_length=240)
