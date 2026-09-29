import uuid

from pydantic import BaseModel, Field

from app.models.enums import Unit


class ShopCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    city_id: uuid.UUID | None = None
    latitude: float | None = None
    longitude: float | None = None
    delivery_prefecture_ids: list[uuid.UUID] = []


class ShopOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    rating_avg: float
    is_verified_badge: bool

    model_config = {"from_attributes": True}


class PriceTierIn(BaseModel):
    min_qty: float = Field(gt=0)
    unit_price_fcfa: int = Field(gt=0)


class ProductCreate(BaseModel):
    variety: str = Field(min_length=2, max_length=80)
    description: str | None = None
    caliber: str | None = None
    unit: Unit = Unit.KG
    unit_price_fcfa: int = Field(gt=0)
    stock_qty: float = Field(ge=0)
    photos: list[str] = Field(default=[], max_length=5)
    price_tiers: list[PriceTierIn] = []


class ProductUpdate(BaseModel):
    description: str | None = None
    unit_price_fcfa: int | None = Field(default=None, gt=0)
    stock_qty: float | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ProductOut(BaseModel):
    id: uuid.UUID
    shop_id: uuid.UUID
    variety: str
    description: str | None
    unit: Unit
    unit_price_fcfa: int
    stock_qty: float
    photos: list[str] | None
    is_active: bool

    model_config = {"from_attributes": True}
