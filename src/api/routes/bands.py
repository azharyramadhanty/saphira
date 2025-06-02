from typing import Annotated
from fastapi import APIRouter, HTTPException, Path, Query, Depends
from src.enums.band import Genre
from src.models.band import Band, BandCreate, BandResponse, Album
# from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.database.session import get_async_session


# BANDS = [
#     {'id': 1, 'name': 'kiss', 'genre': 'Metal'},
#     {'id': 2, 'name': 'the beatles', 'genre': 'Rock', 'albums': [
#         {'title': 'abbey road', 'release_date': '1966-05-02'},
#     ]},
#     {'id': 3, 'name': 'queen', 'genre': 'Progressive Rock', 'albums': [
#         {'title': 'bohemian rhapsody', 'release_date': '1975-07-03'},
#         {'title': 'the game', 'release_date': '1980-10-15'},
#     ]},
# ]

router = APIRouter(prefix="/bands", tags=["bands"])


@router.get('/', response_model=list[BandResponse])
async def get_all_bands(
    genre: Genre | None = None,
    name: Annotated[str | None, Query(max_length=10)] = None,
    session: AsyncSession = Depends(get_async_session)
    # has_albums: bool = False
) -> any:
    # iterate each row  in bands then convert it to Band pydantic model
    # band_list = [Band(**b) for b in BANDS]
    query = select(Band).options(selectinload(Band.albums))
    if genre:
        # band_list = [b for b in band_list if b.genre.value.lower() == genre.value.lower()]
        query = query.where(Band.genre == genre)

    if name:
        # band_list = [b for b in band_list if name.lower() in b.name.lower()]
        query = query.where(Band.name.ilike(f"%{name}%"))
    # if has_albums:
    #     band_list = [b for b in band_list if len(b.albums) > 0]
    result = await session.execute(query)
    return result.scalars().all()


@router.get('/{band_id}', response_model=BandResponse)
async def get_detail_band(
    band_id: Annotated[int, Path(title="the band id")],
    session: AsyncSession = Depends(get_async_session)
) -> any:
    result = await session.execute(
        select(Band).options(selectinload(
            Band.albums)).filter(Band.id == band_id)
    )
    band = result.scalars().first()
    # band = next((Band(**b) for b in BANDS if b['id'] == band_id), None)
    if band is None:
        raise HTTPException(status_code=404, detail='Band not found')
    return band


@router.post('/', response_model=BandResponse)
async def create_band(
    band_data: BandCreate,
    session: AsyncSession = Depends(get_async_session)
) -> any:
    band = Band(name=band_data.name, genre=band_data.genre)
    session.add(band)

    if band_data.albums:
        for album in band_data.albums:
            album_obj = Album(
                title=album.title, release_date=album.release_date, band=band
            )
            session.add(album_obj)

    await session.commit()
    await session.refresh(band)
    query = select(Band).options(selectinload(
        Band.albums)).filter(Band.id == band.id)
    result = await session.execute(query)
    band = result.scalars().first()
    #  new_id = BANDS[-1]['id'] + 1
    # # dump all the band_data model convery it into dict
    # band = Band(id=new_id, **band_data.model_dump()).model_dump()
    # BANDS.append(band)
    return band
