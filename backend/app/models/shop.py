import uuid

from datetime import datetime

from sqlalchemy import Column, Enum, Float, ForeignKey, Integer, JSON, Numeric, String, Table, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import Unit
from app.models.mixins import Timestamps, UUIDPk

shop_delivery_zones = Table(
    "shop_delivery_zones",
    Base.metadata,
    Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), primary_key=True),
    Column("prefecture_id", UUID(as_uuid=True), ForeignKey("prefectures.id"), primary_key=True),
)


class Shop(UUIDPk, Timestamps, Base):
    __tablename__ = "shops"
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)
    cover_url: Mapped[str | None] = mapped_column(String(500))
    city_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("cities.id"))
    latitude: Mapped[float | None] = mapped_column(Float)   # -> PostGIS Geography en v1.1
    longitude: Mapped[float | None] = mapped_column(Float)
    opening_hours: Mapped[dict | None] = mapped_column(JSON)  # jours/horaires de disponibilité
    is_verified_badge: Mapped[bool] = mapped_column(default=False)
    rating_avg: Mapped[float] = mapped_column(Float, default=0.0)

    products: Mapped[list["Product"]] = relationship(back_populates="shop")


class Product(UUIDPk, Timestamps, Base):
    """Une annonce = une variété d'igname (Laboko, Kokouvi, Danto, Ahoun…)."""
    __tablename__ = "products"
    shop_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    variety: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    caliber: Mapped[str | None] = mapped_column(String(60))
    unit: Mapped[Unit] = mapped_column(Enum(Unit), default=Unit.KG)
    unit_price_fcfa: Mapped[int] = mapped_column(Integer)          # FCFA : pas de décimales
    stock_qty: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    low_stock_threshold: Mapped[float] = mapped_column(Numeric(10, 2), default=10)
    photos: Mapped[list | None] = mapped_column(JSON)              # max 5 URLs
    is_active: Mapped[bool] = mapped_column(default=True)
    featured_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # mise en avant payante
    is_moderated_ok: Mapped[bool] = mapped_column(default=True)

    shop: Mapped[Shop] = relationship(back_populates="products")
    price_tiers: Mapped[list["PriceTier"]] = relationship(cascade="all, delete-orphan", lazy="selectin")


class PriceTier(UUIDPk, Base):
    """Prix dégressif pour commandes en gros."""
    __tablename__ = "product_price_tiers"
    product_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("products.id"))
    min_qty: Mapped[float] = mapped_column(Numeric(10, 2))
    unit_price_fcfa: Mapped[int] = mapped_column(Integer)
