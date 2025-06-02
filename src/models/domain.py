from sqlmodel import Field
from src.database.base import Base


class Domain(Base, table=True):
    __table_args__ = {"schema": "public"}

    domain_id: str = Field(primary_key=True, max_length=240)
    client_id: str | None = Field(
        default=None, max_length=20, foreign_key="public.client.client_id")
