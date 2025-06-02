from datetime import date
from sqlmodel import Field
from src.database.base import Base


class Client(Base, table=True):
    __table_args__ = {"schema": "public"}

    client_id: str = Field(primary_key=True, max_length=20)
    client_name: str = Field(default=None, max_length=40)
    desk_name: str | None = Field(default=None, max_length=40)
    desk_email: str | None = Field(default=None, max_length=240)
    validity_start: date | None = None
    validity_end: date | None = None
    faq_example: str | None = None
