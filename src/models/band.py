from datetime import date
from pydantic import BaseModel
from src.enums.band import Genre
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator


class AlbumBase(SQLModel):
    title: str
    release_date: date


class Album(AlbumBase, table=True):
    id: int = Field(default=None, primary_key=True)
    band_id: int | None = Field(default=None, foreign_key="band.id")
    band: "Band" = Relationship(back_populates="albums")


class BandBase(SQLModel):
    name: str
    genre: Genre


class Band(BandBase, table=True):
    id: int = Field(default=None, primary_key=True)
    albums: list['Album'] = Relationship(back_populates="band")

    @field_validator("genre", mode="before")
    def title_case_genre(cls, value):  # pylint: disable=no-self-argument
        return value.title() if isinstance(value, str) else value.value


class BandResponse(BaseModel):
    id: int
    name: str
    genre: Genre
    albums: list['Album'] | None = []

    class Config:
        orm_mode = True  # This enables `.from_orm()` behavior


class BandCreate(BandBase):
    albums: list['AlbumBase'] | None = None
