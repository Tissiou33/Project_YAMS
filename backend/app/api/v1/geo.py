import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.geo import City, Prefecture, Region

router = APIRouter(prefix="/geo", tags=["geo"])


@router.get("/regions")
async def regions(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Region).where(Region.is_active))).scalars().all()
    return [{"id": r.id, "name": r.name} for r in rows]


@router.get("/regions/{region_id}/prefectures")
async def prefectures(region_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(Prefecture).where(Prefecture.region_id == region_id))).scalars().all()
    return [{"id": p.id, "name": p.name} for p in rows]


@router.get("/prefectures/{prefecture_id}/cities")
async def cities(prefecture_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(City).where(City.prefecture_id == prefecture_id))).scalars().all()
    return [{"id": c.id, "name": c.name, "is_urban": c.is_urban} for c in rows]
