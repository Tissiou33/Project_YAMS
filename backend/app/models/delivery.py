import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import DeliveryMode, DeliveryStatus
from app.models.mixins import Timestamps, UUIDPk


class Delivery(UUIDPk, Timestamps, Base):
    __tablename__ = "deliveries"
    order_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), unique=True)
    carrier_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    status: Mapped[DeliveryStatus] = mapped_column(Enum(DeliveryStatus), default=DeliveryStatus.PROPOSED)
    mode: Mapped[DeliveryMode] = mapped_column(Enum(DeliveryMode), default=DeliveryMode.LOCAL)
    distance_km: Mapped[float | None] = mapped_column(Float)
    fee_fcfa: Mapped[int] = mapped_column(default=0)
    current_lat: Mapped[float | None] = mapped_column(Float)   # suivi GPS (urbain en priorité)
    current_lng: Mapped[float | None] = mapped_column(Float)
    incident: Mapped[str | None] = mapped_column(String(300))  # client absent, adresse erronée, produit endommagé
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
