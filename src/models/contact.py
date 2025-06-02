from datetime import date
from sqlmodel import Field
from src.database.base import Base


class Contact(Base, table=True):
    __table_args__ = {"schema": "public"}

    id: str = Field(primary_key=True, max_length=40)
    client_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.client.client_id")
    contact_id: str | None = Field(default=None, max_length=5)
    stream: str | None = Field(default=None, max_length=40)
    sub_stream: str | None = Field(default=None, max_length=40)
    contact_name: str | None = Field(default=None, max_length=40)
    contact_email: str | None = Field(default=None, max_length=240)
    contact_phone: str | None = Field(default=None, max_length=40)
    created_date: date | None = None
    changed_date: date | None = None
