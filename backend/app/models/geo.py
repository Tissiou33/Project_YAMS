import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import UUIDPk


class Region(UUIDPk, Base):
    """Maritime, Plateaux, Centrale, Kara, Savanes — paramétrable en back-office."""
    __tablename__ = "regions"
    name: Mapped[str] = mapped_column(String(80), unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)  # déploiement progressif
    prefectures: Mapped[list["Prefecture"]] = relationship(back_populates="region")


class Prefecture(UUIDPk, Base):
    __tablename__ = "prefectures"
    name: Mapped[str] = mapped_column(String(80))
    region_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("regions.id"))
    region: Mapped[Region] = relationship(back_populates="prefectures")
    cities: Mapped[list["City"]] = relationship(back_populates="prefecture")


class City(UUIDPk, Base):
    """Ville / village / quartier (niveau le plus fin, extensible)."""
    __tablename__ = "cities"
    name: Mapped[str] = mapped_column(String(80))
    is_urban: Mapped[bool] = mapped_column(default=False)  # impacte les frais de livraison
    prefecture_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("prefectures.id"))
    prefecture: Mapped[Prefecture] = relationship(back_populates="cities")
